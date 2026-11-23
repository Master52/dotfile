"""Run with .venv/bin/python -m unittest -v from amazon_pdf."""
from collections import Counter
from contextlib import chdir
import hashlib
from unittest.mock import patch
from contextlib import redirect_stderr
from io import StringIO
from types import SimpleNamespace
from pathlib import Path
import re
import tempfile
import unittest

import pymupdf as pdf
import amazon_labels as app


def compact(text):
    return re.sub(r'\s+', '', text)


class ProductTests(unittest.TestCase):
    def test_title_preserves_variant_and_pack_size(self):
        raw = 'Brand Board (9MM, 12x18 Inch) | Pack of 2 | B0GWQGKWXP ( seller-code )\nHSN:441233'
        self.assertEqual(app.product_name(raw), 'Brand Board (9MM, 12x18 Inch) | Pack of 2')

    def test_multiline_seller_code_removed(self):
        raw = 'Brand Wall Art - Black & Gold | B0GWDSM44D (\nWall-Art-12x24-FBM )\nHSN:3926'
        self.assertEqual(app.product_name(raw), 'Brand Wall Art - Black & Gold')

    def test_ambiguous_title_rejected(self):
        with self.assertRaises(app.LayoutError):
            app.product_name('Unrecognized title without invoice identifiers')

    def test_quantity_is_ordered_units_not_pack_contents(self):
        label = app.Label(b'', 1216, 1824, [app.Product('Widget (Pack of 2)', 3)], 1, 'top')
        rows = app.grouped_products([(Path('one.pdf'), [label, label])])
        self.assertEqual(rows[0]['quantity'], 6)
        self.assertEqual(rows[0]['parcels'], 2)

    def test_long_title_rejected_instead_of_truncated(self):
        fontfiles = app.load_fonts()
        font = pdf.Font(fontfile=str(fontfiles[0]))
        with pdf.open() as doc:
            page = doc.new_page()
            page.insert_font(fontname='normal', fontfile=str(fontfiles[0]))
            with self.assertRaises(app.LayoutError):
                app.write_fitted(page, pdf.Rect(0, 0, 100, 20), 'Very long product name ' * 100, font)

    def test_unknown_page_layout_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'wrong.pdf'
            with pdf.open() as doc:
                doc.new_page(width=300, height=400)
                doc.save(source)
            with self.assertRaises(app.LayoutError):
                app.extract_labels(source)


class MergedProductTests(unittest.TestCase):
    def invoice(self, *, same=False, same_name=False, missing_quantity=False,
                misaligned=False, incomplete=False, invalid_quantity=False):
        document = pdf.open()
        self.addCleanup(document.close)
        page = document.new_page(width=595, height=842)
        xs, ys = [316, 326, 450, 480, 490, 594], [200, 214, 286, 320, 340]
        for left, right in zip(xs, xs[1:]):
            page.draw_rect(pdf.Rect(left, 200, right, 214), color=None, fill=(.9, .9, .9))
        for x in xs:
            for top, bottom in zip(ys, ys[1:]):
                if top == 320 and x not in (316, 594):
                    continue  # Amazon's TOTAL cell spans the product columns.
                page.draw_line((x, top), (x, bottom), width=.3)
        for y in ys:
            page.draw_line((316, y), (594, y), width=.3)

        def put(x, y, text):
            page.insert_text((x, y), text, fontsize=6)

        for x, title in [(317, 'No'), (327, 'Description'), (451, 'Price'),
                         (481, 'Qty'), (495, 'Amount')]:
            put(x, 209, title)
        put(320, 225, '1')
        put(327, 225, 'Widget A')
        put(327, 233, '| B012345678 ( sku-a )')
        put(327, 241, 'HSN:1234')
        put(327, 257, 'Widget A' if same or same_name else 'Widget B')
        put(327, 265, '| B012345678 ( sku-a )' if same else '| B012345679 ( sku-b )')
        if not incomplete:
            put(327, 273, 'HSN:1234')
        put(482, 248 if misaligned else 233, '0' if invalid_quantity else '1')
        if not missing_quantity:
            put(482, 265, '2')
        put(320, 295, '2')
        put(327, 295, 'Widget C')
        put(327, 303, '| B012345680 ( sku-c )')
        put(327, 311, 'HSN:1234')
        put(482, 303, '3')
        put(316, 328, 'TOTAL:')
        return page

    def parse(self, page, fast):
        if fast:
            return app.bordered_products(page, 0, page.get_drawings(), page.get_textpage())
        return app.invoice_products(page, 0)

    def test_different_products_and_following_numbered_row(self):
        page = self.invoice()
        for fast in (True, False):
            with self.subTest(fast=fast):
                self.assertEqual(self.parse(page, fast), [app.Product('Widget A', 1),
                    app.Product('Widget B', 2), app.Product('Widget C', 3)])

    def test_identical_products_are_combined(self):
        page = self.invoice(same=True)
        for fast in (True, False):
            with self.subTest(fast=fast):
                self.assertEqual(self.parse(page, fast), [app.Product('Widget A', 3),
                                                         app.Product('Widget C', 3)])

    def test_same_title_with_different_identifiers_stays_separate(self):
        page = self.invoice(same_name=True)
        self.assertEqual(self.parse(page, True), [app.Product('Widget A', 1),
                         app.Product('Widget A', 2), app.Product('Widget C', 3)])

    def test_business_invoice_supports_merged_products(self):
        page = self.invoice()
        document = page.parent
        page.insert_text((30, 30), 'Tax Invoice/Bill of Supply/Cash Memo\nPage 1 of 2')
        document.new_page(pno=0, width=595, height=842)
        second = document.new_page(width=595, height=842)
        second.insert_text((30, 30), 'Tax Invoice/Bill of Supply/Cash Memo\nPage 2 of 2')
        self.assertEqual(app.business_invoice_products(document, 0),
                         [app.Product('Widget A', 1), app.Product('Widget B', 2),
                          app.Product('Widget C', 3)])

    def test_uncertain_merged_rows_are_rejected(self):
        for option in ('missing_quantity', 'misaligned', 'incomplete', 'invalid_quantity'):
            page = self.invoice(**{option: True})
            for fast in (True, False):
                with self.subTest(option=option, fast=fast), self.assertRaises(app.LayoutError):
                    self.parse(page, fast)

    def test_merged_different_products_render_with_their_own_quantities(self):
        products = self.parse(self.invoice(), True)
        pixmap = pdf.Pixmap(pdf.csGRAY, pdf.IRect(0, 0, 1216, 1824), False)
        pixmap.clear_with(255)
        label = app.Label(pixmap.tobytes('png'), 1216, 1824, products, 1, 'top')
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'different-products.pdf'
            app.render_labels([label], path, app.load_fonts())
            with pdf.open(path) as rendered:
                text = rendered[0].get_text()
                self.assertIn('3 PRODUCTS | TOTAL QTY: 6', text)
                for name, quantity in [('Widget A', 1), ('Widget B', 2), ('Widget C', 3)]:
                    self.assertIn(f'[{quantity}x] {name}', text)

    def test_reported_pdf_and_render_preserve_shipping_images(self):
        source = Path('/home/master/Downloads/157191160787020763.pdf')
        if not source.is_file():
            self.skipTest('Merged-row invoice sample is not present.')
        before = hashlib.sha256(source.read_bytes()).digest()
        labels = app.extract_labels(source)
        self.assertEqual([sum(p.quantity for p in label.products) for label in labels], [1, 1, 2])
        self.assertEqual(len(labels[-1].products), 1)
        self.assertIn('Trolley', labels[-1].products[0].name)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'fixed.pdf'
            app.main([str(source), '-o', str(output)])
            with pdf.open(output) as rendered:
                self.assertEqual(len(rendered), 1)
                self.assertIn('QTY: 2', rendered[0].get_text())
                expected = Counter(pdf.Pixmap(label.image).digest for label in labels)
                actual = Counter(image['digest'] for page in rendered
                                 for image in page.get_image_info(hashes=True))
                self.assertEqual(actual, Counter({digest: count * 2 for digest, count in expected.items()}))
        self.assertEqual(before, hashlib.sha256(source.read_bytes()).digest())


class SampleIntegrationTests(unittest.TestCase):
    def test_business_order_with_two_invoice_pages(self):
        source = Path('/home/master/Downloads/156714370282020757.pdf')
        if not source.is_file():
            self.skipTest('Business invoice sample is not present.')
        labels = app.extract_labels(source)
        self.assertEqual(len(labels), 11)
        self.assertEqual((labels[-1].page, labels[-1].half), (6, 'top'))
        self.assertEqual(labels[-1].products[0].quantity, 1)
        self.assertIn('Trolley', labels[-1].products[0].name)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'labels.pdf'
            app.main([str(source), '-o', str(output)])
            with pdf.open(output) as rendered:
                self.assertEqual(len(rendered), 3)
                self.assertNotIn('Payment Transaction', ''.join(p.get_text() for p in rendered))
            with pdf.open(source) as original:
                # Two distinct standalone labels with their own two-page invoices,
                # surrounded by regular two-label pages. Reusing invoice details
                # here isolates page consumption from product title differences.
                mixed = Path(temporary) / 'mixed.pdf'
                with pdf.open() as document:
                    document.insert_pdf(original, from_page=0, to_page=0)
                    document.insert_pdf(original, from_page=5, to_page=7)
                    label_image = next(image for image in original[1].get_image_info(xrefs=True)
                                       if image['width'] == 1216 and image['bbox'][1] < 421)
                    page = document.new_page(width=595, height=842)
                    page.insert_image(pdf.Rect(label_image['bbox']),
                                      stream=original.extract_image(label_image['xref'])['image'])
                    document.insert_pdf(original, from_page=6, to_page=7)
                    document.insert_pdf(original, from_page=2, to_page=2)
                    document.save(mixed)
                mixed_labels = app.extract_labels(mixed)
                self.assertEqual([label.page for label in mixed_labels], [1, 1, 2, 5, 8, 8])
                self.assertEqual(mixed_labels[2].products, labels[-1].products)
                self.assertEqual(mixed_labels[3].products, labels[-1].products)
                mixed_output = Path(temporary) / 'mixed-labels.pdf'
                app.main([str(mixed), '-o', str(mixed_output)])
                with pdf.open(mixed_output) as rendered:
                    self.assertEqual(len(rendered), 2)
                for name, indices in [('missing', [5, 6]), ('reversed', [5, 7, 6]),
                                      ('wrong-invoice', [5, 0, 7])]:
                    malformed = Path(temporary) / (name + '.pdf')
                    with pdf.open() as document:
                        for index in indices:
                            document.insert_pdf(original, from_page=index, to_page=index)
                        document.save(malformed)
                    with self.subTest(name=name), self.assertRaises(app.LayoutError):
                        app.extract_labels(malformed)

    def test_current_directory_single_pdf_matches_samples(self):
        expected = {'156518282772020755': (16, 17),
                    '156531200655020755': (9, 12),
                    '156634436466020756': (13, 13)}
        sources = [app.BASE / 'input' / (stem + '.pdf') for stem in expected]
        if not all(source.is_file() for source in sources):
            self.skipTest('Original sample PDFs are not present.')
        before = {source: hashlib.sha256(source.read_bytes()).digest() for source in sources}
        with tempfile.TemporaryDirectory() as temporary, chdir(temporary):
            app.main([str(source) for source in sources])
            self.assertEqual([p.name for p in Path(temporary).iterdir()], ['amazon-labels.pdf'])
            labels = []
            for source in sources:
                extracted = app.extract_labels(source)
                count, units = expected[source.stem]
                self.assertEqual(len(extracted), count)
                self.assertEqual(sum(p.quantity for label in extracted for p in label.products), units)
                labels.extend(extracted)
            original_digests = Counter(pdf.Pixmap(label.image).digest for label in labels)
            with pdf.open('amazon-labels.pdf') as doc:
                self.assertEqual(len(doc), (len(labels) + 3) // 4)
                displayed_digests = Counter()
                for page in doc:
                    self.assertEqual(tuple(page.rect)[2:], app.A4)
                    for image in page.get_image_info(hashes=True):
                        displayed_digests[image['digest']] += 1
                    text = page.get_text()
                    self.assertNotIn('Tax Invoice', text)
                    self.assertNotIn('HSN:', text)
                    self.assertNotIn('₹', text)
                self.assertEqual(displayed_digests, Counter({k: v * 2 for k, v in original_digests.items()}))
                for index, label in enumerate(labels):
                    x, y = index % 2 * 297.5, ((index % 4) // 2) * 421
                    text = doc[index // 4].get_text(clip=pdf.Rect(x, y + 285, x + 297.5, y + 351))
                    for product in label.products:
                        self.assertIn(compact(product.name), compact(text))
                    self.assertIn(f'QTY: {sum(p.quantity for p in label.products)}', text)
        self.assertEqual(before, {source: hashlib.sha256(source.read_bytes()).digest() for source in sources})

    def test_failed_render_keeps_previous_final_and_cleans_temporary_files(self):
        with tempfile.TemporaryDirectory() as temporary, chdir(temporary):
            destination = Path('amazon-labels.pdf')
            with pdf.open() as doc:
                doc.new_page()
                doc.set_metadata({'creator': 'amazon-labels'})
                doc.save(destination)
            before = destination.read_bytes()
            label = app.Label(b'', 1216, 1824, [app.Product('Widget', 1)], 1, 'top')
            with patch.object(app, 'extract_labels', return_value=[label]), patch.object(app, 'render_labels', side_effect=app.LayoutError('render failed')):
                with self.assertRaises(app.LayoutError):
                    app.main(['example.pdf'])
            self.assertEqual(destination.read_bytes(), before)
            self.assertEqual([p.name for p in Path(temporary).iterdir()], ['amazon-labels.pdf'])


class EdgeCaseTests(unittest.TestCase):
    def test_invalid_quantities_rejected(self):
        for quantity in ['0', '-1', '1.5', 'two', '']:
            with self.subTest(quantity=quantity):
                rows = [['No', 'Description', 'Qty'], ['1', 'Widget | B012345678 ( code ) HSN:1', quantity]]
                page = SimpleNamespace(find_tables=lambda **kwargs: SimpleNamespace(tables=[SimpleNamespace(extract=lambda: rows)]))
                with self.assertRaisesRegex(app.LayoutError, 'quantity'):
                    app.invoice_products(page, 0)

    def test_general_detector_does_not_skip_unnumbered_product(self):
        rows = [['No', 'Description', 'Qty'],
                ['1', 'Widget A | B012345678 ( code ) HSN:1', '1'],
                [None, 'Widget B | B012345679 ( other ) HSN:1', '2']]
        page = SimpleNamespace(find_tables=lambda **kwargs: SimpleNamespace(tables=[SimpleNamespace(extract=lambda: rows)]))
        with self.assertRaisesRegex(app.LayoutError, 'row number'):
            app.invoice_products(page, 0)

    def test_multiple_products_render_with_individual_quantities(self):
        pixmap = pdf.Pixmap(pdf.csGRAY, pdf.IRect(0, 0, 1216, 1824), False)
        pixmap.clear_with(255)
        label = app.Label(pixmap.tobytes('png'), 1216, 1824,
                          [app.Product('Widget A (Pack of 2)', 2), app.Product('Widget B - Blue', 1)], 1, 'top')
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'multiple.pdf'
            app.render_labels([label], path, app.load_fonts())
            with pdf.open(path) as doc:
                text = doc[0].get_text()
                self.assertIn('2 PRODUCTS | TOTAL QTY: 3', text)
                self.assertIn('[2x] Widget A (Pack of 2)', text)
                self.assertIn('[1x] Widget B - Blue', text)

    def test_duplicate_input_paths_rejected(self):
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit), patch.object(app, 'extract_labels') as extract:
            app.main(['same.pdf', './same.pdf', '--dry-run'])
        extract.assert_not_called()

    def test_duplicate_labels_across_pdfs_rejected(self):
        label = app.Label(b'same image', 1216, 1824, [app.Product('Widget', 1)], 1, 'top')
        with patch.object(app, 'extract_labels', return_value=[label]):
            with self.assertRaisesRegex(app.LayoutError, 'Duplicate shipping label'):
                app.main(['one.pdf', 'two.pdf', '--dry-run'])

    def test_input_cannot_be_output(self):
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
            app.main(['one.pdf', '-o', 'one.pdf', '--dry-run'])

    def test_unrelated_existing_output_is_protected(self):
        with tempfile.TemporaryDirectory() as temporary, chdir(temporary):
            path = Path('amazon-labels.pdf')
            with pdf.open() as doc:
                doc.new_page()
                doc.set_metadata({'creator': 'some other application'})
                doc.save(path)
            before = path.read_bytes()
            with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
                app.main(['example.pdf'])
            self.assertEqual(path.read_bytes(), before)

    def test_encrypted_pdf_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'locked.pdf'
            with pdf.open() as doc:
                doc.new_page(width=595, height=842)
                doc.save(path, encryption=pdf.PDF_ENCRYPT_AES_256, owner_pw='owner', user_pw='password')
            with self.assertRaisesRegex(app.LayoutError, 'Password-protected'):
                app.extract_labels(path)

    def test_empty_pdf_fails_without_output(self):
        with tempfile.TemporaryDirectory() as temporary, chdir(temporary):
            path = Path('empty.pdf')
            path.write_bytes(b'')
            with self.assertRaisesRegex(app.LayoutError, 'No output was created'):
                app.main([str(path)])
            self.assertEqual([p.name for p in Path(temporary).iterdir()], ['empty.pdf'])

    def test_missing_font_glyph_rejected_instead_of_lost(self):
        fonts = app.load_fonts()
        font = pdf.Font(fontfile=str(fonts[0]))
        with pdf.open() as doc:
            page = doc.new_page()
            with self.assertRaisesRegex(app.LayoutError, 'unsupported font characters'):
                app.write_fitted(page, pdf.Rect(0, 0, 200, 50), 'Product \U0010ffff', font)

    def test_repeated_product_rows_count_one_parcel(self):
        label = app.Label(b'', 1216, 1824, [app.Product('Widget', 1), app.Product('Widget', 2)], 1, 'top')
        rows = app.grouped_products([(Path('one.pdf'), [label])])
        self.assertEqual(rows[0]['quantity'], 3)
        self.assertEqual(rows[0]['parcels'], 1)

    def test_missing_later_row_border_does_not_silently_drop_item(self):
        words = [(327, 202, 360, 208, 'Description'), (481, 202, 489, 208, 'Qty'),
                 (320, 219, 323, 225, '1'),
                 (327, 218, 449, 225, 'Widget | B012345678 ( code ) HSN:1'),
                 (483, 220, 486, 226, '1'),
                 (320, 250, 323, 256, '2'), (319, 281, 339, 288, 'TOTAL:')]
        rectangles = [(326, 200, 450, 214), (480, 200, 490, 214),
                      (489.6, 214, 490, 240), (479.6, 214, 480, 240),
                      (325.6, 214, 326, 240), (449.6, 214, 450, 240)]
        drawings = [{'type': 'f', 'rect': pdf.Rect(rect)} for rect in rectangles]
        textpage = SimpleNamespace(extractWORDS=lambda: words)
        with self.assertRaisesRegex(app.LayoutError, 'incomplete'):
            app.bordered_products(None, 0, drawings, textpage)


if __name__ == '__main__':
    unittest.main()
