import os, sets, strutils

proc filterFile(inputFilename, outputFilename: string) =
  let inputFile = open(inputFilename)
  defer: inputFile.close()
  var outputFile = open(outputFilename, fmWrite)
  defer: outputFile.close()
  let allowedProperties = ["name", "devices"].toHashSet()
  var
    inAllowedList = false
    needsDash = false
  for line in inputFile.lines:
    var keepLine = false
    if line.startsWith("- \""):
      let parts = line.split("\"", 3)
      if parts[1] in allowedProperties:
        keepLine = true
      else:
        needsDash = true
        continue
    if inAllowedList and not line.startsWith("  -"):
      inAllowedList = false
    if not line.startsWith("  "):
      keepLine = true
    elif inAllowedList and line.startsWith("  -"):
      keepLine = true
    elif line.startsWith("  \""):
      let parts = line.split("\"", 3)
      if parts[1] in allowedProperties:
        keepLine = true
        if needsDash:
          outputFile.writeLine("- " & line[2..^1])
          needsDash = false
          continue
        if line.endsWith(":"):
          inAllowedList = true
    if keepLine: outputFile.writeLine(line)

proc main() =
  let 
    objectType = "device"
    inputFilename = "device_small.yaml"
    outputFilename = "device_small_filtered.yaml"
  try:
    filterFile(inputFilename, outputFilename)
  except IOError:
    echo "Error: ", getCurrentExceptionMsg()

when isMainModule:
  main()
