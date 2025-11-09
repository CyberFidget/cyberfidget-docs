CF Guide Annotator Starter
==========================

Files:
- cf-guide-annotator.html — Open in your browser. Load an image, click to add pins, Shift+Drag to draw boxes, export JSON.
- guide.js — Drop into your docs site; it renders annotations for images when you place a special HTML comment under an image.
- guide.css — Optional minimal styles.
- sample-index.md — Example Markdown showing how to reference the JSON.
- sample-image.annot.json — Example annotations file.

How to wire into your site (vanilla):
1) Ensure your Markdown-to-HTML pipeline leaves HTML comments intact.
2) Include guide.css and guide.js in your docs layout/template.
3) For each image to annotate, include a comment immediately after the image:
   <!-- guide:annot src="./my-photo.annot.json" -->
4) Place the .annot.json alongside the image.
