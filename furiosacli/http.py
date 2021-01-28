from furiosacli import consts, __version__

headers = {
    consts.FURIOSA_API_VERSION_HEADER: consts.FURIOSA_API_VERSION_VALUE,  # version 2
    consts.FURIOSA_SDK_VERSION_HEADER: __version__
}
