-- C editing uses built-in features; Minuet supplies Gemini completion.
vim.opt.termguicolors = true
vim.opt.runtimepath:append(vim.fn.expand('~/.vim'))
pcall(vim.cmd.colorscheme, 'desktop')
vim.api.nvim_create_autocmd('FocusGained', {
  callback = function() pcall(vim.cmd.colorscheme, 'desktop') end,
  desc = 'Refresh desktop colors',
})
vim.cmd('filetype plugin indent on')
vim.cmd('syntax enable')
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.wrap = true
vim.opt.linebreak = true
vim.opt.breakindent = true
-- Move through visible rows of wrapped text; counts still move actual lines.
vim.keymap.set('n', 'j', function() return vim.v.count == 0 and 'gj' or 'j' end, { expr = true })
vim.keymap.set('n', 'k', function() return vim.v.count == 0 and 'gk' or 'k' end, { expr = true })
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.incsearch = true
vim.opt.hlsearch = true
vim.opt.splitright = true
vim.opt.splitbelow = true
vim.opt.wildmenu = true
vim.opt.completeopt = { 'menu', 'menuone', 'noselect' }
vim.opt.complete = { '.', 'w', 'b', 'u', 'i' }
vim.g.mapleader = ' '
require('shortcut_guide').setup()
require('markdown_setup').setup()

vim.api.nvim_create_autocmd('FileType', {
  pattern = { 'c', 'cpp' },
  callback = function()
    vim.bo.expandtab = true
    vim.bo.shiftwidth = 4
    vim.bo.softtabstop = 4
    vim.bo.tabstop = 4
    vim.bo.cindent = true
    vim.bo.omnifunc = 'ccomplete#Complete'
    vim.opt_local.path:append({ '/usr/local/include', '/usr/include' })
  end,
})

local function build()
  if vim.bo.buftype ~= '' or vim.fn.expand('%:e') ~= 'c' then
    vim.notify('Open a C source file first.', vim.log.levels.WARN)
    return
  end
  vim.cmd('update')
  local source = vim.api.nvim_buf_get_name(0)
  local dir = vim.fs.dirname(source)
  local root = vim.fs.root(dir, { 'GNUmakefile', 'makefile', 'Makefile' })
  local command, executable
  if root then
    command = 'make -C ' .. vim.fn.shellescape(root)
  else
    local compiler = vim.fn.executable('gcc') == 1 and 'gcc' or 'clang'
    if vim.fn.executable(compiler) ~= 1 then
      vim.notify('Install GCC or Clang to compile C.', vim.log.levels.ERROR)
      return
    end
    executable = vim.fn.fnamemodify(source, ':r')
    command = compiler .. ' -std=c17 -Wall -Wextra -Wpedantic -g '
      .. vim.fn.shellescape(source) .. ' -o ' .. vim.fn.shellescape(executable)
  end
  local previous = vim.bo.makeprg
  vim.bo.makeprg = command
  local ok, err = pcall(vim.cmd, 'silent make!')
  local status = vim.v.shell_error
  vim.bo.makeprg = previous
  if not ok then
    vim.notify(tostring(err), vim.log.levels.ERROR)
    return
  end
  if #vim.fn.getqflist() > 0 then vim.cmd('botright copen') else vim.cmd('cclose') end
  if status ~= 0 then
    vim.notify('Build failed. Inspect :copen for diagnostics.', vim.log.levels.ERROR)
    return
  end
  vim.notify('Build succeeded' .. (root and ' (Makefile)' or ''))
  return { executable = executable, dir = dir }
end

local function run()
  local result = build()
  if not result then return end
  local executable = result.executable
  if not executable then
    executable = vim.fn.input('Makefile executable (relative to source directory): ', '', 'file')
    if executable == '' then return end
    executable = vim.fn.fnamemodify(result.dir .. '/' .. executable, ':p')
  end
  if vim.fn.executable(executable) ~= 1 then
    vim.notify('Executable not found: ' .. executable, vim.log.levels.ERROR)
    return
  end
  vim.cmd('botright new')
  vim.fn.jobstart({ executable }, { term = true, cwd = result.dir })
  vim.cmd('startinsert')
end
vim.api.nvim_create_user_command('CBuild', build, { desc = 'Build C file or nearest Makefile' })
vim.api.nvim_create_user_command('CRun', run, { desc = 'Build and run C program' })
vim.keymap.set('n', '<F5>', '<cmd>CBuild<CR>', { desc = 'Build C' })
vim.keymap.set('n', '<F6>', '<cmd>CRun<CR>', { desc = 'Build and run C' })
-- Tree-style file browser in a left sidebar; open files in the editing window.
vim.g.netrw_banner = 0
vim.g.netrw_liststyle = 3
vim.g.netrw_browse_split = 4
vim.g.netrw_altv = 1
vim.g.netrw_winsize = 10
vim.keymap.set('n', '<leader>e', '<cmd>Lexplore 28<CR>', { desc = 'Toggle file sidebar' })
vim.keymap.set('n', '<leader>n', '<cmd>cnext<CR>', { desc = 'Next diagnostic' })
vim.keymap.set('n', '<leader>p', '<cmd>cprevious<CR>', { desc = 'Previous diagnostic' })
vim.keymap.set('n', '<leader>h', '<cmd>nohlsearch<CR>', { desc = 'Clear search highlighting' })
vim.keymap.set('t', '<Esc><Esc>', '<C-\\><C-n>', { desc = 'Leave terminal input mode' })

-- Restore the existing Gemini completion configuration.
local gemini = require('gemini_setup')
gemini.setup()

-- Minuet is installed as a native Neovim package; no plugin manager is needed.
vim.cmd.packadd('minuet-ai.nvim')
require('minuet').setup({
  provider = 'gemini',
  context_window = 12000,
  n_completions = 1,
  debounce = 700,
  throttle = 3000,
  request_timeout = 15,
  notify = 'warn',
  enable_predicates = {
    function()
      if not gemini.key() or vim.bo.buftype ~= '' or vim.bo.filetype == '' then return false end
      local name = vim.fs.basename(vim.api.nvim_buf_get_name(0)) or ''
      if vim.api.nvim_buf_get_name(0) == require('shortcut_guide').path then return false end
      return not (name == '.env' or name:match('^%.env%.') or name:match('%.pem$') or name:match('%.key$'))
    end,
  },
  provider_options = {
    gemini = {
      model = vim.env.GEMINI_MODEL or 'gemini-3.5-flash-lite',
      api_key = gemini.key,
      stream = true,
      optional = {
        generationConfig = {
          maxOutputTokens = 512,
          thinkingConfig = {thinkingLevel = 'minimal'},
        },
      },
    },
  },
  virtualtext = {
    auto_trigger_ft = {'*'},
    keymap = {
      accept_line = '<C-g><C-j>',
      next = '<C-g><C-n>',
      prev = '<C-g><C-p>',
      dismiss = '<C-]>',
    },
  },
})

vim.keymap.set('i', '<Tab>', function()
  local action = require('minuet.virtualtext').action
  if action.is_visible() then
    action.accept()
    return ''
  end
  return '<Tab>'
end, {expr = true, silent = true, desc = 'Accept AI suggestion or insert Tab'})

vim.api.nvim_create_user_command('AIToggle', function()
  require('minuet.virtualtext').action.toggle_auto_trigger()
end, {desc = 'Toggle automatic AI suggestions for this buffer'})

vim.api.nvim_create_autocmd('VimEnter', {
  once = true,
  callback = function()
    if not gemini.key() then
      vim.notify('AI completion is installed. Run :GeminiSetup to enter your API key.', vim.log.levels.INFO)
    end
  end,
})


vim.api.nvim_set_hl(0, "MinuetVirtualText", { link = "Comment" })
vim.api.nvim_create_autocmd("ColorScheme", {
  callback = function() vim.api.nvim_set_hl(0, "MinuetVirtualText", { link = "Comment" }) end,
})
