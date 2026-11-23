local M = {}
M.path = vim.fn.expand('~/.config/bspwm/SHORTCUTS.md')

function M.open()
  vim.cmd.edit(vim.fn.fnameescape(M.path))
end

function M.search()
  M.last_result = nil
  M.open()
  if vim.fn.executable('fzf') ~= 1 then
    vim.notify('fzf is unavailable; use / to search this guide.', vim.log.levels.WARN)
    return
  end
  local target_buffer, target_window = vim.api.nvim_get_current_buf(), vim.api.nvim_get_current_win()
  local input, output = vim.fn.tempname(), vim.fn.tempname()
  local entries, section = {}, 'Guide'
  for number, line in ipairs(vim.api.nvim_buf_get_lines(target_buffer, 0, -1, false)) do
    if line:match('^#+ ') then section = line:gsub('^#+ ', '') end
    if line:match('%S') and not line:match('^| ?%-') then
      entries[#entries + 1] = number .. '\t' .. section .. '  ' .. line
    end
  end
  vim.fn.writefile(entries, input)
  vim.cmd('botright 18new')
  local picker_buffer = vim.api.nvim_get_current_buf()
  vim.bo.bufhidden = 'wipe'
  local command = 'fzf --no-multi --delimiter="\t" --with-nth=2.. --layout=reverse '
    .. '--prompt="Find shortcut> " --header="Type app + action; Enter jumps; Esc cancels" '
    .. '< ' .. vim.fn.shellescape(input) .. ' > ' .. vim.fn.shellescape(output)
  vim.fn.jobstart({ 'sh', '-c', command }, {
    term = true,
    on_exit = function(_, code)
      vim.schedule(function()
        local selected = vim.fn.filereadable(output) == 1 and vim.fn.readfile(output)[1] or ''
        M.last_result = { code = code, selected = selected }
        vim.fn.delete(input)
        vim.fn.delete(output)
        if vim.api.nvim_buf_is_valid(picker_buffer) then
          vim.api.nvim_buf_delete(picker_buffer, { force = true })
        end
        if vim.api.nvim_win_is_valid(target_window) then vim.api.nvim_set_current_win(target_window) end
        if code == 0 and selected then
          local number = tonumber(selected:match('^(%d+)\t'))
          if number and vim.api.nvim_buf_is_valid(target_buffer) then
            vim.api.nvim_win_set_buf(0, target_buffer)
            vim.api.nvim_win_set_cursor(0, { number, 0 })
            vim.cmd('normal! zz')
          end
        end
      end)
    end,
  })
  vim.cmd.startinsert()
end

function M.setup()
  vim.api.nvim_create_user_command('Shortcuts', M.open, { desc = 'Open desktop and application shortcut guide' })
  vim.api.nvim_create_user_command('ShortcutSearch', M.search, { desc = 'Fuzzy search shortcut guide' })
  vim.api.nvim_create_autocmd('BufEnter', {
    pattern = M.path,
    callback = function(args)
      vim.keymap.set('n', '<leader>/', M.search, { buffer = args.buf, desc = 'Fuzzy search all shortcuts' })
      vim.keymap.set('n', '<leader>ff', M.search, { buffer = args.buf, desc = 'Fuzzy search all shortcuts' })
    end,
  })
end

return M
