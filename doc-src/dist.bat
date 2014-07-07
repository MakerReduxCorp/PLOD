DEL -R ..\docs\*.*
COPY build\html\*.html ..\docs
MKDIR ..\docs\_sources
MKDIR ..\docs\_static
COPY build\html\_sources ..\docs\_sources
COPY build\html\_static ..\docs\_static
COPY build\epub\PLOD.epub ..\docs
