$s=(New-Object -COM WScript.Shell).CreateShortcut("$env:USERPROFILE\Desktop\GitHubDownloader.lnk")
$s.TargetPath="C:\temp\velvet-sojourner\dist\GitHubDownloader.exe"
$s.WorkingDirectory="C:\temp\velvet-sojourner\dist"
$s.Description="GitHub Repo Downloader"
$s.Save()
Write-Host "Shortcut created on Desktop"