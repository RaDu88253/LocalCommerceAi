pip freeze | Out-File -FilePath requirements.txt -Encoding utf8
# The usual pip freeze > requirements.txt command in PowerShell breaks UTF-8 encoding.