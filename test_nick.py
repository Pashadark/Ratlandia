import sys
sys.path.append('/root/bot')
from database import get_rating
r = get_rating(185185047)
print(f"rating = {r}")
print(f"nickname = {r.get('nickname') if r else 'NO RATING'}")
