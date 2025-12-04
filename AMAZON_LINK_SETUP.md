# Amazon Product Link Setup Guide

This guide explains how to add product-specific Amazon links to your video descriptions.

## Overview

Each video can have its own Amazon product link that will be automatically included in the descriptions for YouTube, Instagram, and TikTok. If no product link is found, the system will use your general creator link from `.env`.

## Method 1: Filename Format (Recommended for Automation)

Include the Amazon link directly in the video filename.

### Example with Shortened Link (amzn.to) - Recommended

**Your link:** `https://amzn.to/3K7euOO`

**Filename format:**

```
product-review_https-amzn-to-3K7euOO.mp4
```

**How to convert:**

1. Start with: `https://amzn.to/3K7euOO`
2. Replace `://` with `-`: `https-amzn.to/3K7euOO`
3. Replace `.` with `-`: `https-amzn-to/3K7euOO`
4. Replace `/` with `-`: `https-amzn-to-3K7euOO`
5. Add to filename: `product-review_https-amzn-to-3K7euOO.mp4`

### Example with Full Amazon Link

**Your link:** `https://www.amazon.com/dp/B08XYZ1234`

**Filename format:**

```
product-review_https-amazon-com-dp-B08XYZ1234.mp4
```

**Quick conversion rules:**

- `https://` → `https-`
- `.` → `-` (dots become hyphens)
- `/` → `-` (slashes become hyphens)

The system will automatically:

- Extract the link from the filename
- Convert it back to a proper URL
- Use it in all platform descriptions

**Tip:** Shortened links (amzn.to) are shorter and easier to work with in filenames!

## Method 2: Sidecar Files (Easiest Manual Method)

Create a text file with the same name as your video, but with `.amazon`, `.link`, or `.txt` extension.

**Example:**

- Video: `product-review.mp4`
- Link file: `product-review.amazon` or `product-review.link`

**Content of the file:**

```
https://www.amazon.com/dp/B08XYZ1234
```

Just paste the full Amazon URL in the file (one line).

## Method 3: JSON Mapping File (Best for Batch Processing)

Create a `video_links.json` file in your `storage/inputs` folder.

**Format:**

```json
{
  "product-review": "https://www.amazon.com/dp/B08XYZ1234",
  "another-video": "https://www.amazon.com/dp/B09ABC5678",
  "video-name.mp4": "https://www.amazon.com/dp/B10DEF9012"
}
```

You can use either:

- Video name without extension: `"product-review"`
- Full filename: `"product-review.mp4"`

## Priority Order

The system checks in this order:

1. **Filename format** (Method 1)
2. **Sidecar files** (Method 2)
3. **JSON mapping** (Method 3)
4. **Fallback**: General creator link from `.env`

## How It Appears in Descriptions

### YouTube Description:

```
https://www.amazon.com/dp/B08XYZ1234

https://www.amazon.com/shop/YOUR_CREATOR_NAME

#AmazonReview #ProductReview ...
```

### Instagram Caption:

```
https://www.amazon.com/dp/B08XYZ1234

#AmazonReview #ProductReview ...
```

### TikTok Caption:

```
https://www.amazon.com/dp/B08XYZ1234

#AmazonReview #ProductReview ...
```

## Examples

### Example 1: Filename Method (Shortened Link)

```
storage/inputs/
  └── bluetooth-speaker-review_https-amzn-to-3K7euOO.mp4
```

This will use: `https://amzn.to/3K7euOO`

### Example 1b: Filename Method (Full Link)

```
storage/inputs/
  └── bluetooth-speaker-review_https-amazon-com-dp-B08XYZ1234.mp4
```

### Example 2: Sidecar File Method

```
storage/inputs/
  ├── bluetooth-speaker-review.mp4
  └── bluetooth-speaker-review.amazon
```

Content of `bluetooth-speaker-review.amazon`:

```
https://www.amazon.com/dp/B08XYZ1234
```

### Example 3: JSON Mapping Method

```
storage/inputs/
  ├── video_links.json
  └── bluetooth-speaker-review.mp4
```

Content of `video_links.json`:

```json
{
  "bluetooth-speaker-review": "https://www.amazon.com/dp/B08XYZ1234"
}
```

## Tips

1. **For batch processing**: Use Method 3 (JSON file) - easiest to manage multiple videos
2. **For single videos**: Use Method 2 (sidecar file) - quick and simple
3. **For automation**: Use Method 1 (filename) - if you can rename files programmatically

## Troubleshooting

**Link not appearing?**

- Check that the link contains "amazon" (case-insensitive)
- Verify the file/format matches one of the methods above
- Check the console output - it will show if a link was found

**Wrong link format?**

- Make sure URLs start with `http://` or `https://`
- Full Amazon URLs work best (e.g., `https://www.amazon.com/dp/PRODUCTID`)
