# Consulting Page Deployment

## Quick Deploy (Netlify)
1. Drag this folder into https://app.netlify.com/drop
2. Custom domain: Settings > Domain management
3. Forms: Add `netlify` attribute to `<form>` tags

## Or use Netlify CLI
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=.
```

## Before Launch Checklist
- [ ] Update Calendly link in index.html (search for calendly.com)
- [ ] Update email address (ashlee69r@gmail.com)
- [ ] Add Google Analytics or Plausible script
- [ ] Test on mobile
- [ ] Set up contact form endpoint (Formspree/Netlify Forms)
