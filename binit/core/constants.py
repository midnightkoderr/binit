from pathlib import Path

VERSION = '0.1.0'

SUPPORTED_PLATFORMS = {'linux'}

ARCH_ALIASES = {
    'amd64': {'amd64', 'x86_64', 'x64', 'x86-64', '64bit', '64-bit'},
    '386': {'386', 'i386', 'i686', 'x86', '32bit', '32-bit'},
    'arm64': {'arm64', 'aarch64', 'armv8'},
    'armv7': {'armv7', 'armhf'},
    'armv6': {'armv6'},
    'ppc64le': {'ppc64le'},
    's390x': {'s390x'}
}

DEFAULT_BASE_DIR = Path.home() / '.binit'
