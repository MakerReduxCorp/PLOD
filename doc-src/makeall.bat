@ECHO OFF

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set BUILDDIR=build
set ALLSPHINXOPTS=-d %BUILDDIR%/doctrees %SPHINXOPTS% source
set I18NSPHINXOPTS=%SPHINXOPTS% source
if NOT "%PAPER%" == "" (
	set ALLSPHINXOPTS=-D latex_paper_size=%PAPER% %ALLSPHINXOPTS%
	set I18NSPHINXOPTS=-D latex_paper_size=%PAPER% %I18NSPHINXOPTS%
)

%SPHINXBUILD% -b html %ALLSPHINXOPTS% %BUILDDIR%/html
if errorlevel 1 exit /b 1
echo.
echo.Build finished for html. The HTML pages are in %BUILDDIR%/html.

%SPHINXBUILD% -b epub %ALLSPHINXOPTS% %BUILDDIR%/epub
if errorlevel 1 exit /b 1
echo.
echo.Build finished for epub. The epub file is in %BUILDDIR%/epub.

%SPHINXBUILD% -b rst %ALLSPHINXOPTS% %BUILDDIR%/rst
if errorlevel 1 exit /b 1
echo.
echo.Build finished for rst. The rst files are in %BUILDDIR%/rst.
