local M = {}

local function target_at_cursor()
  local line = vim.api.nvim_get_current_line()
  local col = vim.api.nvim_win_get_cursor(0)[2] + 1
  local start = 1
  while true do
    local first, last, label, destination = line:find('(%b[])(%b())', start)
    if not first then break end
    if col >= first and col <= last then
      destination = vim.trim(destination:sub(2, -2))
      return destination:match('^<(.-)>')
        or destination:gsub('%s+["\'].*$', '')
    end
    start = last + 1
  end
  start = 1
  while true do
    local first, last, destination = line:find('%[%[(.-)%]%]', start)
    if not first then break end
    if col >= first and col <= last then
      local path = destination:match('^[^|]+')
      local file, anchor = path:match('^(.-)(#.*)$')
      file = file or path
      if file ~= '' and not vim.fs.basename(file):match('%.') then file = file .. '.md' end
      return file .. (anchor or '')
    end
    start = last + 1
  end
end

function M.open()
  local target = target_at_cursor()
  if not target then
    vim.notify('Place the cursor on a Markdown link.', vim.log.levels.INFO)
    return
  end
  if target:match('^%a[%w+.-]*:') and not target:match('^file:') then
    vim.ui.open(target)
    return
  end
  local path = target:gsub('^file://', ''):gsub('#.*$', '')
  path = path:gsub('%%(%x%x)', function(hex) return string.char(tonumber(hex, 16)) end)
  path = path:gsub('\\([%p])', '%1')
  if path == '' then return end
  if path:sub(1, 1) == '~' then path = vim.fn.expand(path) end
  if not vim.startswith(path, '/') then
    path = vim.fs.dirname(vim.api.nvim_buf_get_name(0)) .. '/' .. path
  end
  path = vim.fs.normalize(path)
  local ok, err = pcall(function()
    vim.fn.mkdir(vim.fs.dirname(path), 'p')
    if not vim.uv.fs_stat(path) then
      local fd, reason = vim.uv.fs_open(path, 'wx', 420)
      if not fd then error(reason) end
      vim.uv.fs_close(fd)
    end
    vim.cmd.edit(vim.fn.fnameescape(path))
  end)
  if not ok then vim.notify(tostring(err), vim.log.levels.ERROR) end
end

return M
