import ccsyspath


LOG_PATH = "/tmp/codeplag.log"
SUPPORTED_EXTENSIONS = {
    'py': [
        r'.py\b'
    ],
    'cpp': [
        r'.cpp\b',
        r'.c\b',
        r'.h\b'
    ]
}
COMPILE_ARGS = '-x c++ --std=c++11'.split()
SYSPATH = ccsyspath.system_include_paths('clang++')
INCARGS = [b'-I' + inc for inc in SYSPATH]
COMPILE_ARGS = COMPILE_ARGS + INCARGS
