local M = {}

local function list_marker(buffer, item)
  local line = vim.api.nvim_buf_get_lines(buffer, item.range.row_start, item.range.row_start + 1, false)[1] or ''
  local indent = #(line:match('^%s*') or '')
  local depth = math.floor(indent / math.max(vim.bo[buffer].shiftwidth, 1)) % 3 + 1
  return {
    text = ({ '●', '○', '▪' })[depth],
    hl = 'MarkdownBullet' .. depth,
    add_padding = true,
    conceal_on_checkboxes = true,
  }
end

local function markdown_colors()
  local colors = { '#f38ba8', '#fab387', '#f9e2af', '#a6e3a1', '#89dceb', '#cba6f7' }
  for level, color in ipairs(colors) do
    for _, group in ipairs({ '@markup.heading.' .. level .. '.markdown', 'markdownH' .. level }) do
      vim.api.nvim_set_hl(0, group, { fg = color, bold = true })
    end
  end
  local groups = {
    ['@markup.strong'] = { fg = '#f9e2af', bold = true },
    ['@markup.italic'] = { fg = '#cba6f7', italic = true },
    ['@markup.link'] = { fg = '#89b4fa', underline = true },
    ['@markup.link.url'] = { fg = '#89dceb', underline = true },
    ['@markup.raw'] = { fg = '#a6e3a1', bg = '#303630' },
    markdownBold = { fg = '#f9e2af', bold = true },
    markdownItalic = { fg = '#cba6f7', italic = true },
    markdownCode = { fg = '#a6e3a1', bg = '#303630' },
    markdownUrl = { fg = '#89dceb', underline = true },
    MarkdownBullet1 = { fg = '#fab387', bold = true },
    MarkdownBullet2 = { fg = '#89dceb', bold = true },
    MarkdownBullet3 = { fg = '#cba6f7', bold = true },
    MarkdownListNumber = { fg = '#89b4fa', bold = true },
    ['@markup.list.markdown'] = { fg = '#89b4fa', bold = true },
    MarkviewCheckboxUnchecked = { fg = '#f38ba8', bold = true },
    MarkviewCheckboxChecked = { fg = '#a6e3a1', bold = true },
    MarkviewCheckboxPending = { fg = '#f9e2af', bold = true },
    MarkviewCheckboxProgress = { fg = '#89dceb', bold = true },
  }
  for group, opts in pairs(groups) do vim.api.nvim_set_hl(0, group, opts) end
  require('markview.highlights').setup()
  for level, color in ipairs(colors) do
    vim.api.nvim_set_hl(0, 'MarkviewPalette' .. level, { fg = color, bg = '#303630', bold = true })
    vim.api.nvim_set_hl(0, 'MarkviewPalette' .. level .. 'Fg', { fg = color })
    vim.api.nvim_set_hl(0, 'MarkviewPalette' .. level .. 'Sign', { fg = color })
    vim.api.nvim_set_hl(0, 'MarkviewHeading' .. level, { link = 'MarkviewPalette' .. level })
    vim.api.nvim_set_hl(0, 'MarkviewHeading' .. level .. 'Sign', { link = 'MarkviewPalette' .. level .. 'Sign' })
  end
  vim.api.nvim_set_hl(0, 'MarkviewInlineCode', { fg = '#a6e3a1', bg = '#303630' })
end

function M.setup()
  vim.cmd.packadd('markview.nvim')
  require('markview').setup({
    markdown = {
      list_items = {
        indent_size = 2,
        shift_width = 2,
        marker_minus = list_marker,
        marker_plus = list_marker,
        marker_star = list_marker,
        marker_dot = { hl = 'MarkdownListNumber' },
        marker_parenthesis = { hl = 'MarkdownListNumber' },
      },
    },
    preview = {
      map_gx = false,
      icon_provider = 'internal',
      modes = { 'n', 'no', 'c', 'i' },
      hybrid_modes = { 'i' },
    },
  })
  markdown_colors()
  local group = vim.api.nvim_create_augroup('MarkdownPreviewRefresh', { clear = true })
  local pending = false
  local function refresh()
    if pending then return end
    pending = true
    vim.defer_fn(function()
      pending = false
      markdown_colors()
      -- Respect buffers where the user has turned preview off.
      require('markview.commands').Render()
      require('markview.actions').splitview_render()
    end, 60)
  end
  vim.api.nvim_create_autocmd({ 'VimEnter', 'ColorScheme', 'VimResized', 'WinResized', 'FocusGained' }, {
    group = group,
    callback = refresh,
    desc = 'Restore Markdown highlights and preview after theme or display changes',
  })
  vim.api.nvim_create_autocmd({ 'InsertLeave', 'TextChanged', 'BufWinEnter' }, {
    group = group,
    callback = function(args)
      if vim.bo[args.buf].filetype == 'markdown' then refresh() end
    end,
    desc = 'Restore Markdown preview after edits',
  })
  vim.api.nvim_create_autocmd('FileType', {
    pattern = 'markdown',
    callback = function()
      vim.opt_local.conceallevel = 2
      vim.opt_local.concealcursor = 'nc'
      vim.opt_local.expandtab = true
      vim.opt_local.shiftwidth = 2
      vim.opt_local.softtabstop = 2
      vim.opt_local.wrap = true
      for _, key in ipairs({ '<CR>', 'gf', 'gx' }) do
        vim.keymap.set('n', key, require('markdown_links').open,
          { buffer = true, desc = 'Open Markdown link or create target file' })
      end
      vim.keymap.set('n', '<leader>mt', '<cmd>Markview toggle<CR>',
        { buffer = true, desc = 'Toggle Markdown preview' })
      vim.keymap.set('n', '<leader>ms', '<cmd>Markview splitToggle<CR>',
        { buffer = true, desc = 'Toggle Markdown split preview' })
    end,
  })
  -- Kitty graphics require an interactive UI; keep headless and other terminals usable.
  if #vim.api.nvim_list_uis() > 0 and (vim.env.KITTY_WINDOW_ID or vim.env.TERM == 'xterm-kitty') then
    vim.cmd.packadd('image.nvim')
    require('image').setup({
      backend = 'kitty',
      processor = 'magick_cli',
      integrations = {
        markdown = { enabled = true, download_remote_images = true, clear_in_insert_mode = true },
      },
      max_width = 80,
      max_height = 20,
      max_height_window_percentage = 40,
      editor_only_render_when_focused = true,
      tmux_show_only_in_active_window = true,
    })
  end
end

return M
