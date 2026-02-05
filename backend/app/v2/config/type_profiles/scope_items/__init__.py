from . import industrial
from . import healthcare
from . import hospitality
from . import restaurant

SCOPE_ITEM_PROFILE_SOURCES = [
    industrial.SCOPE_ITEM_PROFILES,
    healthcare.SCOPE_ITEM_PROFILES,
    hospitality.SCOPE_ITEM_PROFILES,
    restaurant.SCOPE_ITEM_PROFILES,
]

SCOPE_ITEM_DEFAULT_SOURCES = [
    industrial.SCOPE_ITEM_DEFAULTS,
    healthcare.SCOPE_ITEM_DEFAULTS,
    hospitality.SCOPE_ITEM_DEFAULTS,
    restaurant.SCOPE_ITEM_DEFAULTS,
]
