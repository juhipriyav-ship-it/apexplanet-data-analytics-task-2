@echo off
REM ==========================================================================
REM  ApexPlanet Data Analytics - Task 5
REM  Runs the full Superstore automated pipeline, then rebuilds the PDF report.
REM  Double-click this file, or schedule it with Windows Task Scheduler.
REM ==========================================================================

setlocal
cd /d "%~dp0"

echo [1/2] Running automated pipeline...
python "scripts\automate_pipeline.py"
if errorlevel 1 goto :error

echo.
echo [2/2] Building the final PDF report...
python "scripts\build_report.py"
if errorlevel 1 goto :error

echo.
echo ==========================================================================
echo  SUCCESS - pipeline outputs and Task5_Final_Report.pdf are up to date.
echo ==========================================================================
endlocal
exit /b 0

:error
echo.
echo ==========================================================================
echo  ERROR - a step failed. Review the output above.
echo ==========================================================================
endlocal
exit /b 1

REM ==========================================================================
REM  WINDOWS TASK SCHEDULER (how to register this batch file)
REM --------------------------------------------------------------------------
REM  Run ONE of the commands below from an elevated Command Prompt.
REM
REM  Daily at 07:00:
REM    schtasks /Create /TN "ApexPlanet_Task5_Pipeline" /TR "\"%~dp0run_pipeline.bat\"" /SC DAILY /ST 07:00 /F
REM
REM  Weekly (every Monday) at 07:00:
REM    schtasks /Create /TN "ApexPlanet_Task5_Pipeline" /TR "\"%~dp0run_pipeline.bat\"" /SC WEEKLY /D MON /ST 07:00 /F
REM
REM  Run it on demand / delete it:
REM    schtasks /Run    /TN "ApexPlanet_Task5_Pipeline"
REM    schtasks /Delete /TN "ApexPlanet_Task5_Pipeline" /F
REM ==========================================================================
