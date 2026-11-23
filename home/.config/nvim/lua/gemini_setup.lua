local M = {}
local uv = vim.uv
local directory = vim.fn.stdpath('data') .. '/credentials'
local keyfile = directory .. '/gemini-api-key'
local saved_key

---@return string?
function M.key()
  local env_key = vim.env.GEMINI_API_KEY or vim.env.GOOGLE_API_KEY
  if env_key and env_key ~= '' then return env_key end
  if saved_key then return saved_key end
  if vim.fn.filereadable(keyfile) == 1 then
    local ok, lines = pcall(vim.fn.readfile, keyfile)
    if ok then
      saved_key = vim.trim(table.concat(lines, ''))
      if saved_key == '' then saved_key = nil end
    end
  end
  return saved_key
end

function M.check()
  local key = M.key()
  if not key then
    vim.notify('Run :GeminiSetup first.', vim.log.levels.WARN)
    return
  end
  local model = require('minuet').config.provider_options.gemini.model
  local url = 'https://generativelanguage.googleapis.com/v1beta/models/' .. model .. ':generateContent'
  local body = vim.json.encode({
    contents = {{parts = {{text = 'Reply with OK.'}}}},
    generationConfig = {maxOutputTokens = 64, thinkingConfig = {thinkingLevel = 'minimal'}},
  })
  vim.notify('Checking Gemini access...', vim.log.levels.INFO)
  -- Supply the credential on stdin so it is absent from the command line.
  local header = 'header = ' .. vim.json.encode('x-goog-api-key: ' .. key) .. '\n'
  vim.system({'curl', '--silent', '--show-error', '--max-time', '30',
    '--config', '-', '--header', 'Content-Type: application/json',
    '--data-binary', body, url}, {text = true, stdin = header}, vim.schedule_wrap(function(result)
      local ok, data = pcall(vim.json.decode, result.stdout or '')
      if result.code ~= 0 or not ok then
        vim.notify('Gemini connection failed. Check your internet connection.', vim.log.levels.ERROR)
      elseif data.error then
        vim.notify('Gemini check failed: ' .. (data.error.status or tostring(data.error.code))
          .. '. Check your key, model access, billing or quota in AI Studio.', vim.log.levels.ERROR)
      elseif data.candidates then
        vim.notify('Gemini is connected. Inline suggestions are ready.', vim.log.levels.INFO)
      else
        vim.notify('Gemini returned no completion. Try :GeminiCheck again.', vim.log.levels.WARN)
      end
    end))
end

function M.setup()
  vim.api.nvim_create_user_command('GeminiSetup', function()
    local ok, value = pcall(vim.fn.inputsecret, 'Gemini API key (hidden): ')
    if not ok then return end
    value = vim.trim(value)
    local quote = value:sub(1, 1)
    if (quote == '"' or quote == "'" or quote == '`') and value:sub(-1) == quote then
      value = vim.trim(value:sub(2, -2))
    end
    if value == '' then return end
    -- Key formats can contain punctuation. Reject only whitespace and bytes
    -- outside printable ASCII; the API validates the actual credential.
    if value:find('[^!-~]') then
      vim.notify('The key contains spaces or non-printable characters. Copy the key again from AI Studio.', vim.log.levels.ERROR)
      return
    end
    vim.fn.mkdir(directory, 'p', 448)
    uv.fs_chmod(directory, 448)
    local stat = uv.fs_lstat(keyfile)
    if stat and stat.type ~= 'file' then
      vim.notify('The credential path must be a regular file.', vim.log.levels.ERROR)
      return
    end
    if stat then uv.fs_chmod(keyfile, 384) end
    local fd = uv.fs_open(keyfile, 'w', 384)
    if not fd then
      vim.notify('Could not save the API key.', vim.log.levels.ERROR)
      return
    end
    local written = uv.fs_write(fd, value .. '\n', 0)
    uv.fs_close(fd)
    if not written then
      vim.notify('Could not save the API key.', vim.log.levels.ERROR)
      return
    end
    saved_key = value
    -- A newly entered key takes precedence over an inherited key for this session.
    vim.env.GEMINI_API_KEY = nil
    vim.env.GOOGLE_API_KEY = nil
    vim.notify('API key saved with owner-only permissions.', vim.log.levels.INFO)
    M.check()
  end, {desc = 'Enter a Gemini API key using a masked prompt'})
  vim.api.nvim_create_user_command('GeminiCheck', M.check, {desc = 'Check Gemini API access'})
  vim.api.nvim_create_user_command('GeminiStatus', function()
    local model = require('minuet').config.provider_options.gemini.model
    vim.notify('Gemini key: ' .. (M.key() and 'configured' or 'missing') .. '\nModel: ' .. model)
  end, {desc = 'Show Gemini configuration without displaying the key'})
end

return M
