@echo off
rem -------------------------------------------------------------------
rem  jsony-reader.cmd — Windows batch wrapper for jsony-reader
rem
rem  Usage: jsony-reader <command> [options...]
rem
rem  This wrapper finds jsony-reader (Python script) in the same
rem  directory as this .cmd file, so it works without installing.
rem -------------------------------------------------------------------
setlocal
set "SCRIPT_DIR=%~dp0"
python "%SCRIPT_DIR%jsony-reader" %*
endlocal
