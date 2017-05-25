$invocation = (Get-Variable MyInvocation).Value
$directorypath = Split-Path $invocation.MyCommand.Path
echo 'Packing source...'
cd '.\src\js'
webpack -p
cd $directorypath
echo 'Copying to public...'
cp '.\src\js\bundle.js' '.\public\js\bundle.js'
cp '.\src\css\bundle.css' '.\public\css\bundle.css'
echo 'Completed!'