// usage: osascript -l JavaScript pdf2png.js in.pdf outdir [scale]
ObjC.import('Foundation'); ObjC.import('Quartz'); ObjC.import('AppKit');
function run(argv) {
  var inPath = argv[0], outDir = argv[1], scale = parseFloat(argv[2] || "1.0");
  var first = parseInt(argv[3] || "1"), last = parseInt(argv[4] || "0");
  var url = $.NSURL.fileURLWithPath(inPath);
  var doc = $.PDFDocument.alloc.initWithURL(url);
  var n = doc.pageCount;
  $.NSFileManager.defaultManager.createDirectoryAtPathWithIntermediateDirectoriesAttributesError(outDir, true, $(), null);
  if (last <= 0 || last > n) last = n;
  for (var i = first - 1; i < last; i++) {
    var page = doc.pageAtIndex(i);
    var bounds = page.boundsForBox($.kPDFDisplayBoxMediaBox);
    var w = Math.round(bounds.size.width * scale), h = Math.round(bounds.size.height * scale);
    var rep = $.NSBitmapImageRep.alloc.initWithBitmapDataPlanesPixelsWidePixelsHighBitsPerSampleSamplesPerPixelHasAlphaIsPlanarColorSpaceNameBytesPerRowBitsPerPixel(null, w, h, 8, 4, true, false, $.NSCalibratedRGBColorSpace, 0, 0);
    var ctx = $.NSGraphicsContext.graphicsContextWithBitmapImageRep(rep);
    $.NSGraphicsContext.saveGraphicsState;
    $.NSGraphicsContext.setCurrentContext(ctx);
    var cg = ctx.CGContext;
    $.CGContextSetRGBFillColor(cg, 1, 1, 1, 1);
    $.CGContextFillRect(cg, $.CGRectMake(0, 0, w, h));
    $.CGContextScaleCTM(cg, scale, scale);
    page.drawWithBoxToContext($.kPDFDisplayBoxMediaBox, cg);
    $.NSGraphicsContext.restoreGraphicsState;
    var data = rep.representationUsingTypeProperties($.NSPNGFileType, $());
    var name = "slide-" + String(i + 1).padStart(3, "0") + ".png";
    data.writeToFileAtomically(outDir + "/" + name, true);
  }
  return "wrote pages " + first + "-" + last + " of " + n + " to " + outDir;
}
