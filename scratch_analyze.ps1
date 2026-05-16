$repos = Get-ChildItem 'C:\temp\velvet-sojourner\repos' -Directory
$prefixes = @{}
foreach($r in $repos) {
    $parts = $r.Name -split '_',2
    if($parts.Count -gt 1) {
        $p = $parts[0]
        if($prefixes.ContainsKey($p)){$prefixes[$p]++}else{$prefixes[$p]=1}
    } else {
        if($prefixes.ContainsKey('[no-prefix]')){$prefixes['[no-prefix]']++}else{$prefixes['[no-prefix]']=1}
    }
}
$prefixes.GetEnumerator() | Sort-Object Value -Descending | Format-Table Name, Value -AutoSize
