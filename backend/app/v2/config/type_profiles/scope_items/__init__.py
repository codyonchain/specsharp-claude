from . import civic
from . import industrial
from . import healthcare
from . import hospitality
from . import multifamily
from . import office
from . import recreation
from . import retail
from . import restaurant

CIVIC_SCOPE_ITEM_PROFILE_ALIASES = {
    "civic_baseline_structural_v1": civic.SCOPE_ITEM_PROFILES["civic_library_structural_v1"],
}

SCOPE_ITEM_PROFILE_SOURCES = [
    CIVIC_SCOPE_ITEM_PROFILE_ALIASES,
    civic.SCOPE_ITEM_PROFILES,
    industrial.SCOPE_ITEM_PROFILES,
    healthcare.SCOPE_ITEM_PROFILES,
    hospitality.SCOPE_ITEM_PROFILES,
    multifamily.SCOPE_ITEM_PROFILES,
    office.SCOPE_ITEM_PROFILES,
    recreation.SCOPE_ITEM_PROFILES,
    retail.SCOPE_ITEM_PROFILES,
    restaurant.SCOPE_ITEM_PROFILES,
]

SCOPE_ITEM_DEFAULT_SOURCES = [
    civic.SCOPE_ITEM_DEFAULTS,
    industrial.SCOPE_ITEM_DEFAULTS,
    healthcare.SCOPE_ITEM_DEFAULTS,
    hospitality.SCOPE_ITEM_DEFAULTS,
    multifamily.SCOPE_ITEM_DEFAULTS,
    office.SCOPE_ITEM_DEFAULTS,
    recreation.SCOPE_ITEM_DEFAULTS,
    retail.SCOPE_ITEM_DEFAULTS,
    restaurant.SCOPE_ITEM_DEFAULTS,
]
