$ErrorActionPreference = 'Stop'
$reportRoot = 'E:\xiuxian\论文报告'
$reportDocx = Join-Path $reportRoot '太古仙尊每日助手源码分析报告.docx'
$reportPdf = Join-Path $reportRoot '太古仙尊每日助手源码分析报告.pdf'
$reportWord = $null
$reportDoc = $null
try {
    $reportWord = New-Object -ComObject Word.Application
    $reportWord.Visible = $false
    $reportWord.DisplayAlerts = 0
    $reportDoc = $reportWord.Documents.Open($reportDocx, $false, $false)
    $reportDoc.Fields.Update() | Out-Null
    foreach ($reportToc in $reportDoc.TablesOfContents) {
        $reportToc.Update()
        $reportToc.Range.Font.Name = 'Times New Roman'
        $reportToc.Range.Font.NameFarEast = '宋体'
        $reportToc.Range.Font.Size = 12
    }
    $reportDoc.Repaginate()
    $reportDoc.Save()
    $reportDoc.ExportAsFixedFormat($reportPdf, 17)
    'PDF exported; page count: ' + $reportDoc.ComputeStatistics(2)
} finally {
    if ($null -ne $reportDoc) { $reportDoc.Close(0); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($reportDoc) | Out-Null }
    if ($null -ne $reportWord) { $reportWord.Quit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($reportWord) | Out-Null }
}
