#!/usr/bin/env python3
"""Prepare Amazon Easy Ship labels and a product-wise packing list, offline."""
from __future__ import annotations

import argparse
from collections import OrderedDict
import csv
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import sys
import tempfile
import time

import pymupdf as pdf

BASE = Path(__file__).resolve().parent
A4 = (595.0, 842.0)
FONT_DIR = Path('/usr/share/fonts/TTF')


class LayoutError(ValueError):
    pass


@dataclass(frozen=True)
class Product:
    name: str
    quantity: int


@dataclass
class Label:
    image: bytes
    width: int
    height: int
    products: list[Product]
    page: int
    half: str


def product_name(description: str) -> str:
    """Remove invoice identifiers, preserving the complete title and variants."""
    text = ' '.join(description.split())
    text = re.split(r'\bHSN\s*:', text, maxsplit=1, flags=re.I)[0].strip()
    # Amazon's table ends with ASIN (seller SKU). Never strip product parentheses.
    match = re.search(r'\s*\|?\s*\bB0[A-Z0-9]{8}\b\s*\([^)]*\)\s*$', text)
    if not match:
        raise LayoutError('Product title has no recognized ASIN/SKU ending; manual review needed.')
    text = text[:match.start()].strip(' |')
    if not text:
        raise LayoutError('Product name is empty.')
    return text


def row_products(description: str, quantity: str, *, words=None,
                 description_rect=None, quantity_rect=None) -> list[Product]:
    """Match each complete product block to its own vertically aligned quantity."""
    asin = r'\bB0[A-Z0-9]{8}\b'
    if len(re.findall(asin, description)) <= 1:
        if not re.fullmatch(r'[1-9][0-9]*', quantity.strip()):
            raise LayoutError('Invoice contains an invalid or ambiguous item quantity.')
        return [Product(product_name(description), int(quantity))]

    # A merged row needs geometry: never guess quantities from flattened text.
    if words is None or description_rect is None or quantity_rect is None:
        raise LayoutError('Merged product row requires quantity positions for manual-safe extraction.')

    def lines(rect):
        inside = sorted((w for w in words if rect.contains(
            pdf.Point((w[0] + w[2]) / 2, (w[1] + w[3]) / 2))),
            key=lambda w: (w[1], w[0]))
        grouped = []
        for word in inside:
            if not grouped or abs(word[1] - grouped[-1][0][1]) > 1:
                grouped.append([])
            grouped[-1].append(word)
        return [(min(w[1] for w in group), max(w[3] for w in group),
                 ' '.join(w[4] for w in sorted(group, key=lambda w: w[0])))
                for group in grouped]

    blocks, pending = [], []
    for line in lines(description_rect):
        pending.append(line)
        if re.search(r'\bHSN\s*:\s*\d+\b', line[2], re.I):
            blocks.append(pending)
            pending = []
    count = len(re.findall(asin, description))
    if pending or len(blocks) != count:
        raise LayoutError('Merged product descriptions are incomplete or ambiguous.')
    amounts = lines(quantity_rect)
    if len(amounts) != count:
        raise LayoutError('Merged product row has an ambiguous item quantity count.')
    if [line[2] for line in amounts] != quantity.split():
        raise LayoutError('Merged product quantity text does not match its cells.')

    products, used = OrderedDict(), set()
    for block in blocks:
        text = ' '.join(line[2] for line in block)
        if len(re.findall(asin, text)) != 1:
            raise LayoutError('Merged product identifier is ambiguous.')
        name = product_name(text)
        identity = re.search(r'\b(B0[A-Z0-9]{8})\b\s*\(([^)]*)\)', text)
        if identity is None:
            raise LayoutError('Merged product has no recognized ASIN/SKU.')
        top, bottom = min(line[0] for line in block), max(line[1] for line in block)
        matches = [i for i, line in enumerate(amounts)
                   if top - .5 <= (line[0] + line[1]) / 2 <= bottom + .5]
        if len(matches) != 1 or matches[0] in used:
            raise LayoutError('Merged product quantity is not uniquely aligned with its description.')
        index = matches[0]
        amount = amounts[index][2]
        if not re.fullmatch(r'[1-9][0-9]*', amount):
            raise LayoutError('Invoice contains an invalid or ambiguous item quantity.')
        used.add(index)
        # Same name alone is not enough: preserve distinct ASINs, SKUs and variants.
        key = (name, identity[1], ' '.join(identity[2].split()))
        products[key] = products.get(key, 0) + int(amount)
    if len(used) != count:
        raise LayoutError('Merged product row contains unmatched quantities.')
    return [Product(key[0], amount) for key, amount in products.items()]


def detected_row_products(page, table, index, description, quantity, row):
    """Supply cell coordinates only for merged rows in the general detector."""
    title, amount = row[description] or '', row[quantity] or ''
    if len(re.findall(r'\bB0[A-Z0-9]{8}\b', title)) <= 1:
        return row_products(title, amount)
    cells = table.rows[index].cells
    if cells[description] is None or cells[quantity] is None:
        raise LayoutError('Merged product row has missing description or quantity cells.')
    return row_products(title, amount, words=page.get_text('words'),
                        description_rect=pdf.Rect(cells[description]),
                        quantity_rect=pdf.Rect(cells[quantity]))


def bordered_products(page: pdf.Page, top: float, drawings, textpage) -> list[Product]:
    """Read the existing table cells directly, avoiding general table detection."""
    words = textpage.extractWORDS()

    def cell_text(rect):
        inside = [word for word in words
                  if rect.x0 <= (word[0] + word[2]) / 2 <= rect.x1
                  and rect.y0 <= (word[1] + word[3]) / 2 <= rect.y1]
        inside.sort(key=lambda word: (round(word[1], 1), word[0]))
        return ' '.join(word[4] for word in inside)

    headers = {}
    cells = [d['rect'] for d in drawings if d['type'] == 'f'
             and d['rect'].width > 3 and d['rect'].height > 4]
    for title in ['Description', 'Qty']:
        found = [w for w in words if w[4] == title and w[0] > 310
                 and top + 185 < w[1] < top + 405]
        if len(found) != 1:
            raise LayoutError('Unrecognized invoice headers.')
        word = found[0]
        point = pdf.Point((word[0] + word[2]) / 2, (word[1] + word[3]) / 2)
        matches = [r for r in cells if r.contains(point)]
        if not matches:
            raise LayoutError('Missing invoice header cell borders.')
        headers[title] = min(matches, key=lambda r: r.get_area())
    description, quantity = headers['Description'], headers['Qty']
    if abs(description.y1 - quantity.y1) > .5:
        raise LayoutError('Invoice columns are misaligned.')
    vertical = [d['rect'] for d in drawings if d['rect'].width < 1
                and d['rect'].height > 3 and d['rect'].x0 > 310]
    products, boundary, expected_row = [], quantity.y1, 1
    while True:
        right = [r for r in vertical if abs(r.x1 - quantity.x1) < .1
                 and abs(r.y0 - boundary) < .1 and r.y1 < top + 405]
        if not right:
            break
        if len(right) != 1:
            raise LayoutError('Ambiguous product row borders.')
        bottom = right[0].y1
        for edge in [quantity.x0, description.x0, description.x1]:
            if not any(min(abs(r.x0 - edge), abs(r.x1 - edge)) < .1
                       and abs(r.y0 - boundary) < .1 and abs(r.y1 - bottom) < .1
                       for r in vertical):
                raise LayoutError('Missing product cell border.')
        serial = cell_text(pdf.Rect(description.x0 - 9, boundary, description.x0, bottom))
        if not serial.isdigit() and products and 'TOTAL:' in cell_text(pdf.Rect(310, boundary, 594, bottom)):
            break
        amount = cell_text(pdf.Rect(quantity.x0, boundary, quantity.x1, bottom))
        if serial != str(expected_row):
            raise LayoutError('Product row number or quantity is ambiguous.')
        title = cell_text(pdf.Rect(description.x0, boundary, description.x1, bottom))
        products.extend(row_products(title, amount, words=words,
                        description_rect=pdf.Rect(description.x0, boundary, description.x1, bottom),
                        quantity_rect=pdf.Rect(quantity.x0, boundary, quantity.x1, bottom)))
        expected_row += 1
        boundary = bottom
    if not products:
        raise LayoutError('No bordered product rows.')
    if not any(word[4] == 'TOTAL:' and word[0] > 310
               and abs(word[1] - boundary) < 8 for word in words):
        raise LayoutError('Product table is incomplete; its total row was not reached.')
    return products


def invoice_products(page: pdf.Page, top: float, drawings=None, textpage=None) -> list[Product]:
    if drawings is not None and textpage is not None:
        try:
            return bordered_products(page, top, drawings, textpage)
        except LayoutError:
            pass  # Fall back to the general table detector for alternate borders.
    candidates = []
    # Table borders determine columns; never infer quantities from nearby prices.
    for table in page.find_tables(clip=pdf.Rect(310, top + 185, 594, top + 405)).tables:
        rows = table.extract()
        if not rows:
            continue
        header = [' '.join((cell or '').split()) for cell in rows[0]]
        if 'Description' not in header or 'Qty' not in header:
            continue
        description_index, quantity_index = header.index('Description'), header.index('Qty')
        products, expected_row = [], 1
        for index, row in enumerate(rows[1:], 1):
            if not row[0] or not row[0].strip().isdigit():
                if row[description_index] and re.search(r'\bB0[A-Z0-9]{8}\b', row[description_index]):
                    raise LayoutError('Invoice product row has no valid row number.')
                continue
            if int(row[0].strip()) != expected_row:
                raise LayoutError('Invoice product row numbering is incomplete or ambiguous.')
            products.extend(detected_row_products(page, table, index, description_index, quantity_index, row))
            expected_row += 1
        if not products:
            raise LayoutError('Invoice product table has no items.')
        candidates.append(products)
    if len(candidates) != 1:
        raise LayoutError(f'Expected one product table beside the label; found {len(candidates)}.')
    return candidates[0]


def business_invoice_products(document, index: int) -> list[Product]:
    """Read the two full invoice pages immediately after a standalone label."""
    if index + 2 >= len(document):
        raise LayoutError('Standalone label requires two following business invoice pages.')
    pages = [document[index + offset] for offset in (1, 2)]
    for number, page in enumerate(pages, 1):
        text = page.get_text()
        if (page.rotation or abs(page.rect.width - 595) > 1
                or abs(page.rect.height - 842) > 1
                or 'Tax Invoice/Bill of Supply/Cash Memo' not in text
                or not re.search(rf'\bPage\s+{number}\s+of\s+2\b', text)
                or any(image['width'] >= 1000 and image['height'] >= 1500
                       for image in page.get_image_info())):
            raise LayoutError(f'Invalid business invoice page {number} of 2 after standalone label.')
    candidates = []
    for page in pages:
        for table in page.find_tables().tables:
            rows = table.extract()
            if not rows:
                continue
            header = [' '.join((cell or '').split()) for cell in rows[0]]
            if 'Description' not in header or 'Qty' not in header:
                continue
            description, quantity = header.index('Description'), header.index('Qty')
            products, reached_total, expected_row = [], False, 1
            for row_index, row in enumerate(rows[1:], 1):
                if any('TOTAL:' in (cell or '') for cell in row):
                    reached_total = True
                    continue
                title = row[description] or ''
                serial = (row[0] or '').strip()
                if not serial.isdigit():
                    if re.search(r'\bB0[A-Z0-9]{8}\b', title):
                        raise LayoutError('Business invoice product row has no valid row number.')
                    continue
                if reached_total or serial != str(expected_row):
                    raise LayoutError('Business invoice product row number or quantity is ambiguous.')
                products.extend(detected_row_products(page, table, row_index, description, quantity, row))
                expected_row += 1
            if not products or not reached_total:
                raise LayoutError('Business invoice product table is incomplete.')
            candidates.append(products)
    if len(candidates) != 1:
        raise LayoutError(f'Expected one complete business product table; found {len(candidates)}.')
    return candidates[0]


def extract_labels(path: Path) -> list[Label]:
    labels = []
    with pdf.open(path) as document:
        if document.needs_pass:
            raise LayoutError('Password-protected PDF is not supported.')
        consumed = set()
        for index, page in enumerate(document):
            if index in consumed:
                continue
            if page.rotation or abs(page.rect.width - 595) > 1 or abs(page.rect.height - 842) > 1:
                raise LayoutError(f'Page {index + 1}: expected unrotated A4, two-label layout.')
            images = page.get_image_info(xrefs=True)
            drawings = page.get_drawings()
            textpage = page.get_textpage()
            standalone = (len(images) == 1 and not page.get_text().strip()
                          and images[0]['bbox'][0] < 297.5
                          and images[0]['bbox'][1] < 421
                          and images[0]['width'] >= 1000 and images[0]['height'] >= 1500)
            business_products = None
            if standalone:
                business_products = business_invoice_products(document, index)
                consumed.update((index + 1, index + 2))
            for top, half in [(0, 'top'), (421, 'bottom')]:
                found = [image for image in images
                         if 0 <= image['bbox'][0] < 297.5
                         and top <= image['bbox'][1] < top + 421
                         and image['width'] >= 1000 and image['height'] >= 1500]
                if not found:
                    # Only a completely empty half may be skipped.
                    text = page.get_text(clip=pdf.Rect(298, top, 595, top + 421)).strip()
                    any_image = any(i['bbox'][0] < 297.5 and top <= i['bbox'][1] < top + 421
                                    for i in images)
                    if text or any_image:
                        raise LayoutError(f'Page {index + 1}, {half}: missing/unsupported label image.')
                    continue
                if len(found) != 1:
                    raise LayoutError(f'Page {index + 1}, {half}: multiple label images.')
                image = found[0]
                if (image['width'], image['height']) not in {(1216, 1824), (1200, 1800)}:
                    raise LayoutError(f'Page {index + 1}, {half}: unsupported label image dimensions.')
                try:
                    products = business_products if standalone else invoice_products(page, top, drawings, textpage)
                except LayoutError as error:
                    raise LayoutError(f'Page {index + 1}, {half}: {error}') from error
                image_data = document.extract_image(image['xref'])
                if not image_data:
                    raise LayoutError('Unable to extract original shipping label.')
                pixmap = pdf.Pixmap(image_data['image'])
                samples = pixmap.samples_mv
                # Ignore the decorative outside border; the expanded gap must
                # contain no original product/delivery information.
                for row in range(1348, 1500):
                    band = bytes(samples[row * pixmap.stride + 48 * pixmap.n:
                                         row * pixmap.stride + (pixmap.width - 48) * pixmap.n])
                    if band.count(255) != len(band):
                        raise LayoutError(f'Page {index + 1}, {half}: product gap contains original content.')
                labels.append(Label(image_data['image'], image['width'], image['height'],
                                    products, index + 1, half))
    if not labels:
        raise LayoutError('No shipping labels found.')
    return labels


def load_fonts() -> tuple[Path, Path]:
    for directory in [FONT_DIR, Path('/usr/share/fonts/truetype/dejavu')]:
        normal, bold = directory / 'DejaVuSans.ttf', directory / 'DejaVuSans-Bold.ttf'
        if normal.is_file() and bold.is_file():
            return normal, bold
    raise LayoutError('DejaVu Sans regular/bold fonts are required.')


def wrap(text: str, width: float, font: pdf.Font, size: float) -> list[str]:
    lines, current = [], ''
    for word in text.split():
        proposed = (current + ' ' + word).strip()
        if font.text_length(proposed, fontsize=size) <= width:
            current = proposed
        else:
            if current:
                lines.append(current)
                current = ''
            # Wrap long unbroken tokens too; never silently truncate a title.
            for char in word:
                if current and font.text_length(current + char, fontsize=size) > width:
                    lines.append(current)
                    current = ''
                current += char
    if current:
        lines.append(current)
    return lines


def write_fitted(page: pdf.Page, rect: pdf.Rect, text: str, font: pdf.Font,
                 fontname: str = 'normal', preferred: float = 7.5, minimum: float = 6.5):
    unsupported = sorted({ord(char) for char in text if not char.isspace() and not font.has_glyph(ord(char))})
    if unsupported:
        raise LayoutError('Product name contains unsupported font characters: ' +
                          ', '.join(f'U+{code:04X}' for code in unsupported))
    size = preferred
    while size >= minimum - .01:
        lines = wrap(text, rect.width, font, size)
        line_height = size * 1.25
        if len(lines) * line_height <= rect.height:
            baseline = rect.y0 + size
            for line in lines:
                page.insert_text((rect.x0, baseline), line, fontname=fontname, fontsize=size)
                baseline += line_height
            return
        size -= .25
    raise LayoutError('Full product name does not fit legibly in a four-label sheet; manual review needed.')


def render_labels(labels: list[Label], destination: Path, fonts: tuple[Path, Path]):
    normal = pdf.Font(fontfile=str(fonts[0]))
    with pdf.open() as output:
        for number, label in enumerate(labels):
            if number % 4 == 0:
                page = output.new_page(width=A4[0], height=A4[1])
                page.insert_font(fontname='normal', fontfile=str(fonts[0]))
                page.insert_font(fontname='bold', fontfile=str(fonts[1]))
            x, y = (number % 2) * 297.5, ((number % 4) // 2) * 421
            # The source is ONLY the embedded shipping label, never the invoice PDF.
            # Reuse original image pixels; expand its existing blank product gap.
            with pdf.open() as source:
                image_page = source.new_page(width=label.width, height=label.height)
                image_page.insert_image(image_page.rect, stream=label.image)
                width = 250.0
                left = x + (297.5 - width) / 2
                main_height = 1348 * width / label.width
                route_height = (label.height - 1500) * width / label.width
                page.show_pdf_page(pdf.Rect(left, y + 5, left + width, y + 5 + main_height),
                                   source, clip=pdf.Rect(0, 0, label.width, 1348))
                page.show_pdf_page(pdf.Rect(left, y + 352, left + width, y + 352 + route_height),
                                   source, clip=pdf.Rect(0, 1500, label.width, label.height))
            total = sum(item.quantity for item in label.products)
            heading = f'QTY: {total}' if len(label.products) == 1 else f'{len(label.products)} PRODUCTS | TOTAL QTY: {total}'
            head = pdf.Rect(x + 12, y + 287, x + 285.5, y + 302)
            if total > 1:
                page.draw_rect(head, color=(0, 0, 0), fill=(.94, .94, .94), width=1)
            page.insert_text((head.x0 + 4, head.y0 + 11), heading, fontname='bold', fontsize=10)
            description = (' '.join(f'[{item.quantity}x] {item.name}' for item in label.products)
                           if len(label.products) > 1 else label.products[0].name)
            write_fitted(page, pdf.Rect(x + 12, y + 305, x + 285.5, y + 350), description, normal)
        output.set_metadata({'title': 'Amazon Easy Ship labels - full product names',
                             'creator': 'amazon-labels'})
        output.subset_fonts()
        output.save(destination, garbage=4, deflate=True)


def grouped_products(batches: list[tuple[Path, list[Label]]]):
    groups = OrderedDict()
    for _, labels in batches:
        for label in labels:
            parcel_products = set()
            for product in label.products:
                key = product.name.casefold()
                entry = groups.setdefault(key, {'product': product.name, 'quantity': 0, 'parcels': 0})
                entry['quantity'] += product.quantity
                if key not in parcel_products:
                    entry['parcels'] += 1
                    parcel_products.add(key)
    return list(groups.values())


def render_packing_list(batches, destination: Path, fonts):
    products = grouped_products(batches)
    font = pdf.Font(fontfile=str(fonts[0]))
    parcels = sum(len(labels) for _, labels in batches)
    units = sum(row['quantity'] for row in products)
    with pdf.open() as output:
        page, y = None, 900
        for number, row in enumerate(products, 1):
            lines = wrap(row['product'], 420, font, 9)
            height = max(36, len(lines) * 12 + 15)
            if y + height > 795:
                page = output.new_page(width=595, height=842)
                page.insert_font(fontname='normal', fontfile=str(fonts[0]))
                page.insert_font(fontname='bold', fontfile=str(fonts[1]))
                page.insert_text((30, 35), 'PACKING LIST', fontname='bold', fontsize=17)
                page.insert_text((30, 54), f'{parcels} parcels | {units} ordered units | {len(products)} products', fontname='normal', fontsize=10)
                page.insert_text((30, 71), 'Quantity counts ordered packs/units; pack contents remain in the product name.', fontname='normal', fontsize=7.5)
                page.insert_text((30, 95), '#   PRODUCT / VARIANT', fontname='bold', fontsize=9)
                page.insert_text((502, 95), 'QTY', fontname='bold', fontsize=9)
                page.insert_text((30, 819), f'Page {len(output)} | Sources: {len(batches)} PDFs', fontname='normal', fontsize=8)
                y = 105
            page.draw_rect(pdf.Rect(30, y + 5, 38, y + 13), color=(0, 0, 0), width=.6)
            page.insert_text((43, y + 12), str(number), fontname='normal', fontsize=8)
            for index, line in enumerate(lines):
                page.insert_text((65, y + 12 + index * 12), line, fontname='normal', fontsize=9)
            page.insert_text((509, y + 14), str(row['quantity']), fontname='bold', fontsize=12)
            page.draw_line((30, y + height - 3), (563, y + height - 3), color=(.75, .75, .75), width=.4)
            y += height
        output.set_metadata({'title': 'Product-wise packing list', 'creator': 'amazon-labels'})
        output.subset_fonts()
        output.save(destination, garbage=4, deflate=True)
    with destination.with_suffix('.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['Product / variant', 'Ordered quantity', 'Parcels'])
        writer.writerows((row['product'], row['quantity'], row['parcels']) for row in products)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='*', type=Path, help='Input PDFs; defaults to input/*.pdf')
    parser.add_argument('-o', '--output', type=Path, default=Path.cwd() / 'amazon-labels.pdf',
                        help='Final PDF path; defaults to amazon-labels.pdf in the current directory')
    extras = parser.add_mutually_exclusive_group()
    extras.add_argument('--packing-list', action='store_true', help='Also create a product-wise packing-list PDF/CSV')
    extras.add_argument('--labels-only', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--dry-run', action='store_true', help='Validate and count without creating output')
    args = parser.parse_args(argv)
    started = time.monotonic()
    paths = args.files or sorted((BASE / 'input').glob('*.pdf'))
    if not paths:
        parser.error('No input PDFs found.')
    if len({path.resolve() for path in paths}) != len(paths):
        parser.error('The same input PDF was supplied more than once.')
    destination = args.output.expanduser().absolute()
    if destination.suffix.lower() != '.pdf':
        parser.error('Output filename must end in .pdf.')
    if destination.resolve() in {path.resolve() for path in paths}:
        parser.error('Output cannot replace an input PDF.')
    if destination.exists():
        with pdf.open(destination) as previous:
            if previous.metadata.get('creator') != 'amazon-labels':
                parser.error('Output already exists and was not created by amazon-labels; choose another filename with -o.')
    fonts = load_fonts()
    batches, errors, seen_labels = [], [], {}
    for path in paths:
        try:
            labels = extract_labels(path)
            for label in labels:
                digest = hashlib.sha256(label.image).digest()
                location = f'{path.name}, page {label.page}, {label.half}'
                if digest in seen_labels:
                    raise LayoutError(f'Duplicate shipping label: {location}; already present in {seen_labels[digest]}.')
                seen_labels[digest] = location
            batches.append((path, labels))
            print(f'{path.name}: {len(labels)} labels -> {(len(labels) + 3) // 4} A4 pages', flush=True)
        except (LayoutError, OSError, RuntimeError) as error:
            errors.append(f'{path.name}: {error}')
    if errors:
        raise LayoutError('\n'.join(errors) + '\nNo output was created. Review these files first.')
    units = sum(p.quantity for _, labels in batches for label in labels for p in label.products)
    parcels = sum(len(labels) for _, labels in batches)
    if args.dry_run:
        print(f'Validated {parcels} labels, {units} ordered units. No output created.')
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    packing = destination.with_name(destination.stem + '-packing-list.pdf')
    if args.packing_list and (packing.exists() or packing.with_suffix('.csv').exists()):
        if not packing.is_file():
            raise LayoutError('Packing-list CSV already exists; choose a different output name with -o.')
        with pdf.open(packing) as previous:
            if previous.metadata.get('creator') != 'amazon-labels':
                raise LayoutError('Packing-list filename is occupied by another PDF; choose a different output name with -o.')
    # Temporary files are automatically removed, including after a failed render.
    # Replace the prior final PDF only after the new one is fully written.
    with tempfile.TemporaryDirectory(prefix='.amazon-labels-', dir=destination.parent) as temporary:
        stage = Path(temporary)
        render_labels([label for _, labels in batches for label in labels], stage / 'labels.pdf', fonts)
        if args.packing_list:
            render_packing_list(batches, stage / 'packing-list.pdf', fonts)
        (stage / 'labels.pdf').replace(destination)
        if args.packing_list:
            (stage / 'packing-list.pdf').replace(packing)
            (stage / 'packing-list.csv').replace(packing.with_suffix('.csv'))
    print(f'Done: {parcels} labels, {units} ordered units in {time.monotonic() - started:.2f}s')
    print(f'Output: {destination}')


if __name__ == '__main__':
    try:
        main()
    except (LayoutError, OSError, RuntimeError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
