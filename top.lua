-- by 
-- カウンタ群
local header_num = {} -- ヘッダ用
local table_num = 0   -- 表用
local code_num = 0    -- リスト用
local fig_num = 0     -- 図用

-- 小細工
local tmpfnote = ""

-- Table to store footnotes, so they can be included at the end.
local notes = {}

-- 表、リスト、図番号を得る (章の子孫なら 表x.x の形)
local function getn(s) 
  local pre = ""
  if header_num[1] ~= nil then
    pre = header_num[1] .. "." 
  end
  if (s == "table" or s == "tbl") then 
    table_num = table_num + 1
    return "表" .. pre .. table_num
  elseif (s == "code" or s == "list") then 
    code_num = code_num + 1
    return "リスト" .. pre .. code_num
  elseif (s == "fig" or s == "img") then 
    fig_num = fig_num + 1
    return "図" .. pre .. fig_num
  end
end

-- 表、リスト、図番号の初期化 (章が変わるとき)
local function initn()
  table_num = 0
  code_num = 0
  fig_num = 0
end

-- Table to store footnotes, so they can be included at the end.
local notes = {}

-- Blocksep is used to separate block elements.
function Blocksep()
  if (tmpfnote ~= "") then
    return (tmpfnote .. "\n")
  else
    return "\n"
  end
end

-- This function is called once for the whole document. Parameters:
-- body is a string, metadata is a table, variables is a table.
-- This gives you a fragment.  You could use the metadata table to
-- fill variables in a custom lua template.  Or, pass `--template=...`
-- to pandoc, and pandoc will add do the template processing as
-- usual.
function Doc(body, metadata, variables)
  local buffer = {}
  local function add(s)
    table.insert(buffer, s)
  end
  add(body)
  if #notes > 0 then
    add('◆→開始:脚注←◆')
    for _,note in pairs(notes) do
      add(note)
    end
    add('◆→終了:脚注←◆')
  end
  return table.concat(buffer,'\n')
end

-- The functions that follow render corresponding pandoc elements.
-- s is always a string, attr is always a table of attributes, and
-- items is always an array of strings (the items in a list).
-- Comments indicate the types of other variables.

function Str(s)
  return s
end

function Space()
  return " "
end

function LineBreak()
  return "\n"
end

function Emph(s)
  return "▲" .. s .. "☆"
end

function Strong(s)
  return "★" .. s .. "☆"
end

function Subscript(s)
  return "◆→開始:下付き文字←◆" .. s .. "◆→終了:下付き文字←◆"
end

function Superscript(s)
  return "◆→開始:上付き文字←◆" .. s .. "◆→終了:下付き文字←◆"
end

function SmallCaps(s)
  return '◆→開始:スモールキャピタル←◆' .. s .. '◆→開始:スモールキャピタル←◆'
end

function Strikeout(s)
  return '◆→開始:打ち消し線←◆' .. s .. '◆→開始:打ち消し線←◆'
end

function Link(s, src, tit)
  return s .. ' : ' .. src -- FIXME?
end

function Image(s, src, tit)
  local buffer = {}
  -- table.insert(buffer, "◆→図キャプション〜〜←◆")
  if tit ~= "" then 
    table.insert(buffer, getn("fig") .. "\t" .. tit)
--  else
--  	table.insert(buffer, getn("fig"))
  end
  table.insert(buffer, "◆→図: " .. src .. "入る←◆")
  return table.concat(buffer,'\n')
end

function CaptionedImage(s, src, tit)
  local buffer = {}
  table.insert(buffer, "◆→図: " .. s .. "入る←◆")
  if tit ~= "" then 
    table.insert(buffer, "◆→図キャプション←◆" .. getn("fig") .. "\t" .. tit)
  end
  return table.concat(buffer,'\n')
end

function Code(s, attr)
  return "△" .. s .. "☆"
end

function InlineMath(s)
  return "◆→開始:inline-math←◆" .. s .. "◆→終了:inline-math←◆"
end

function DisplayMath(s)
  return "\n◆→開始:indep-math←◆\n" .. s .. "\n◆→終了:indep-math←◆\n"
end

function Note(s)
  local num = #notes + 1
  table.insert(notes, '注' .. num .. '\t' .. s)
  -- return the footnote reference, linked to the note.
  return '◆→脚注上付き:注' .. num .. '←◆'
end

function Span(s, attr)
  return s
end

-- FIXME?
function Cite(s, cs)
  local ids = {}
  for _,cit in ipairs(cs) do
    table.insert(ids, cit.citationId)
  end
  return "<span class=\"cite\" data-citation-ids=\"" .. table.concat(ids, ",") ..
    "\">" .. s .. "</span>"
end

function Plain(s)
  return s
end

function Para(s)
  return string.gsub(s, '\n', '')
end

-- lev is an integer, the header level.
function Header(lev, s, attr)
  local function create_num(lev) -- . 区切りの番号作り
    local str = ""
    for i = 1, lev do 
      if i == 1 then
      	str = header_num[1]
      elseif header_num[i] == nil then
        str = str .. ".0"
      else
        str = str .. "." .. header_num[i]
      end
    end
    return str
  end
  -- if lev == 1 then
  -- 	-- 章番号が指定されていた場合はそれを使用する (とりあえず章だけ...)
  --   local str = string.gsub(s, "(%d+)章[%s　	].+", "%1")
  --   if str ~= s then
  --     header_num[lev] = tonumber(str) - 1
  --     s = s.gsub(s, "%d+章(.+)", "%1")
  --   end
  --   initn() -- 表、リスト、図番号の初期化
  -- end
  if header_num[lev] == nil then -- nil なら新規作成
    header_num[lev] = 1
  else      -- 存在すれば incr し、それ以降のレベルの値を初期化
    header_num[lev] = header_num[lev] + 1
    local i = lev + 1
    while(header_num[i] ~= nil) do
      header_num[i] = 0
      i = i + 1
    end
  end
  if lev == 1 then 
    return "■H1■" .. create_num(lev) .. "章\t" .. s
  else 
    return "■H" .. lev .. "■" .. create_num(lev) .. "\t" .. s
  end
end

function BlockQuote(s)
  return "◆→開始:引用←◆\n" .. s .. "\n◆→終了:引用←◆"
end

function HorizontalRule()
  return "◆→水平罫線←◆"
end

function CodeBlock(s, attr)
  -- return "◆→リストキャプション←◆" .. getn("code") .. "\n"
  return "◆→開始:リスト←◆\n" .. s .. "\n◆→終了:リスト←◆"
end

function BulletList(items)
  local buffer = {}
  for _, item in pairs(items) do
    table.insert(buffer, "●\t" .. item)
  end
  return "◆→開始:箇条書き←◆\n" .. table.concat(buffer, "\n") .. "\n◆→終了:箇条書き←◆"
end

function OrderedList(items)
  local buffer = {}
  local i = 1
  for _, item in pairs(items) do
    table.insert(buffer, i .. "\t" .. item)
    i = i + 1
  end
  return "◆→開始:数字箇条書き←◆\n" .. table.concat(buffer, "\n") .. "\n◆→終了:数字箇条書き←◆"
end

-- Revisit association list STackValue instance.
function DefinitionList(items)
  local buffer = {}
  for _,item in pairs(items) do
    for k, v in pairs(item) do
      table.insert(buffer, "" .. k .. "\n\t" .. table.concat(v, "\n"))
    end
  end
  return "◆→開始:見出し付き箇条書き←◆\n" .. table.concat(buffer, "\n") .. "\n◆→開始:見出し付き箇条書き←◆"
end

-- Convert pandoc alignment to something HTML can use.
-- align is AlignLeft, AlignRight, AlignCenter, or AlignDefault.
function html_align(align)
  if align == 'AlignLeft' then
    return 'left'
  elseif align == 'AlignRight' then
    return 'right'
  elseif align == 'AlignCenter' then
    return 'center'
  else
    return 'left'
  end
end

-- Caption is a string, aligns is an array of strings,
-- widths is an array of floats, headers is an array of
-- strings, rows is an array of arrays of strings.
function Table(caption, aligns, widths, headers, rows)
  local buffer = {}
  local function add(s)
    table.insert(buffer, s)
  end
--  add("◆→表キャプション←◆")
  if caption ~= "" then
    add("◆→表キャプション←◆" .. getn("table") .. "\t" .. caption)
  else
    add("◆→表キャプション←◆" .. getn("table"))
  end
  add("◆→開始:表←◆")
  local tmp = {}
  for i, h in pairs(headers) do
    table.insert(tmp, h)
  end
  add(table.concat(tmp, "\t"))
  add("----------")
  for _, row in pairs(rows) do
    tmp = {}
    for i, c in pairs(row) do
      table.insert(tmp, c)
    end
    add(table.concat(tmp, "\t"))
  end
  add("◆→終了:表←◆")
  return table.concat(buffer,'\n')
end

function Div(s, attr)
  return s
end

function DoubleQuoted(s)
  return "\"" .. s .. "\""
end

function RawInline(s)
  return "" -- "☆☆" .. s
end

function SoftBreak(s)
  return ""
end

-- The following code will produce runtime warnings when you haven't defined
-- all of the functions you need for the custom writer, so it's useful
-- to include when you're working on a writer.
local meta = {}
meta.__index =
  function(_, key)
    io.stderr:write(string.format("WARNING: Undefined function '%s'\n",key))
    return function() return "" end
  end
setmetatable(_G, meta)

