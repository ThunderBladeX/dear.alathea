# dear.alathea

A production-ready personal art site with character sheets, commission calculator, and blog. Built with Flask, optimized for performance, and designed to scale.

## What it does

- **Gallery** - Upload art, people can comment and vote
- **Characters** - T-pose base images with clothing you can toggle on/off
- **Blog** - Write posts with previews
- **Commissions** - Calculator with your prices and modifiers
- **Comments** - Threaded discussions with country tags
- **Admin panel** - Upload stuff and manage content

## Architecture

This is a proper Flask application with:
- **Blueprint-based routing** for scalability
- **libsql-client** for Turso database compatibility
- **Environment-based configuration** perfect for Vercel
- **Optimized database queries** (no N+1 problems)
- **Flask application context** for efficient connection management
- **Service layer** for business logic separation

## Complete setup walkthrough

### Step 1: Get the files and install dependencies

```bash
git clone https://github.com/ThunderBladeX/dear.alathea
cd dear.alathea
pip install -r requirements.txt
```

### Step 2: Set environment variables

**For local development:**
```bash
export FLASK_SECRET_KEY=your-secret-key-here
export ADMIN_USERNAME=youradmin
export ADMIN_PASSWORD=yoursecurepassword
# Turso variables optional for local (uses SQLite fallback)
python run.py
```

**For Vercel deployment:**
Set these in your Vercel project settings:
- `FLASK_SECRET_KEY`
- `TURSO_DATABASE_URL`
- `TURSO_AUTH_TOKEN` 
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

### Step 3: Deploy

The app automatically detects if you're running locally (SQLite) or in production (Turso). Just deploy to Vercel and it will use the Turso database.

## Website walkthrough

### Homepage (`/`)
- Split layout with sidebar and tabbed content
- Shows recent gallery images, blog posts, and characters
- Real-time notifications for logged-in users

### Gallery system (`/gallery`)
- Masonry layout with optimized image loading
- Individual image pages with threaded comments
- WebP conversion for faster loading

### Character system (`/ocs`) 
- Folder-style character previews
- T-pose base with stackable clothing items
- Drag-and-drop layer reordering
- Character info and comments

### Blog system (`/blog`)
- AO3-style post previews
- Full post pages with comments
- Featured image support

### Commission calculator (`/commissions`)
- Interactive price calculator
- All your modifiers and pricing tiers
- Contact information and workflow

### Admin panel (`/admin`)
- Upload gallery images, create characters, write blog posts
- Add clothing items to existing characters
- Data export/import for backups
- Usage statistics

## Image requirements

### Required images (add to static/ folder):
- **Profile picture** (`static/profile.jpg`): 300×300px
- **Character decoration** (`static/character_pose.png`): 400-600px wide

### OC system images (upload via admin):
- **Base images**: 800×1200px, consistent across characters
- **Clothing items**: Exactly same size as base image
- **Profile images**: 200×200px for thumbnails

### Other images:
- **Gallery**: Any size (auto-optimized)
- **Blog featured**: 1200×600px recommended

## Mobile optimization

- Touch-friendly 44px+ buttons
- iOS zoom prevention on form inputs
- Responsive layouts for each screen size
- Drag-and-drop works on touch devices
- Optimized images for mobile bandwidth

## Customization

### Commission prices
Edit in `app/routes/api.py`:
```python
base_prices = {
    'bust': 25,      # Your prices
    'half': 40,
    'full': 60
}
```

### Colors and styling
Same CSS variables in `static/style.css`:
```css
:root {
    --primary-cream: #FFF8E7;
    --dusty-rose: #D4A5A5;
    /* etc... */
}
```

### Social links
Update in `templates/commissions.html`

## Security

- Admin credentials from environment variables
- CSRF protection headers
- Input validation and sanitization
- Parameterized database queries prevent SQL injection
- IP tracking for spam prevention
- Secure file uploads with UUID naming

## Troubleshooting

**Import errors:**
Make sure all `__init__.py` files exist in app/ and subdirectories.

**Database connection errors:**
Check that libsql-client is installed and environment variables are set correctly.

**Image optimization fails:**
The app falls back to serving original images if optimization fails.

**Vercel deployment issues:**
Check that `run.py` is the entry point and all environment variables are set.

---

**Happy character creating!** 🎨✨
