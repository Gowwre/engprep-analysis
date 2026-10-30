-- Drop the first H1 and the first H2 from the Markdown body.
-- The HTML template renders them as the report header instead, so the
-- table of contents starts with the numbered sections rather than the title.
local h1_seen = false
local h2_seen = false

function Header(el)
  if el.level == 1 and not h1_seen then
    h1_seen = true
    return {}
  end
  if el.level == 2 and h1_seen and not h2_seen then
    h2_seen = true
    return {}
  end
  return el
end
