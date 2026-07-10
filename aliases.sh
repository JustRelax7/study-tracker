alias pause-study='touch ~/study-tracker/PAUSED'
alias resume-study='rm ~/study-tracker/PAUSED'
alias study-report='python3 ~/study-tracker/report.py'
study() {
    echo " study-report  : Show today's stats and longest streak"
    echo " pause-study   : Manually pause tracking"
    echo " resume-study  : Resume tracking"
    echo " study         : Show this help menu"
    echo "⚙️  Background check: systemctl --user status study-tracker.service"
