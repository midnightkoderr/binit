import platform
from ghapi.all import GhApi

# OS mapping
OS_MAP = {"Linux": "linux", "Darwin": "darwin", "Windows": "windows"}

# Arch aliases — maps canonical name to all known aliases
ARCH_ALIASES = {
    'amd64':   {'amd64', 'x86_64', 'x64', 'x86-64', '64bit', '64-bit'},
    '386':     {'386', 'i386', 'i686', 'x86', '32bit', '32-bit'},
    'arm64':   {'arm64', 'aarch64', 'armv8'},
    'armv7':   {'armv7', 'armhf'},
    'armv6':   {'armv6'},
    'ppc64le': {'ppc64le'},
    's390x':   {'s390x'}
}

def get_canonical_arch(machine: str) -> str | None:
    machine_lower = machine.lower()
    for canonical, aliases in ARCH_ALIASES.items():
        if machine_lower in aliases:
            return canonical
    return None

api = GhApi()

owner = 'gitleaks'
repo = 'gitleaks'

latest_release = api.repos.get_latest_release(owner=owner, repo=repo)
print(latest_release.tag_name, latest_release.name)

for asset in latest_release.assets:
    print(asset.name)
    print(f'  {asset.browser_download_url}')

current_os = OS_MAP.get(platform.system())
current_arch = get_canonical_arch(platform.machine())

if not current_os:
    raise SystemError(f"Unsupported OS: '{platform.system()}'")
if not current_arch:
    raise SystemError(f"Unsupported arch: '{platform.machine()}'")

print(f"\nDetected OS: {current_os}, Arch: {current_arch}")

arch_aliases = ARCH_ALIASES[current_arch]

matched = [
    asset for asset in latest_release.assets
    if current_os in asset.name.lower()
    and any(alias in asset.name.lower() for alias in arch_aliases)
]

if not matched:
    print("No matching asset found.")
else:
    for asset in matched:
        print(f"\nMatched: {asset.name} ({asset.size} bytes)")
        print(f"  Download: {asset.browser_download_url}")
