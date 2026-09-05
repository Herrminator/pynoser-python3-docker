.mode column --widths 0,0,0,0,0,16,40,20

-- .parameter set :threshold "32 * 1024"

select length(text) +  length(summary) as len, length(a.text) as text, length(a.summary) as summary,
       a.id, a.feed_id,
       strftime('%Y-%m-%d %H:%M', a.lastMod, '+' || coalesce(f.expiry, 720) || ' hours', 'localtime') expires,
       substr(a.title, 1, 40) title, substr(f.title, 1, 20) as feed
from   reader_article a join reader_feed f on a.feed_id = f.id
where  len >= coalesce(:threshold, 32 * 1024)
order by len desc
;
