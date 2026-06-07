/**
 * Vercel serverless: public site config for the frontend.
 * Set FORM_EMAIL in Vercel to change the displayed/fallback form address.
 */
const DEFAULT_FORM_EMAIL = 'owenkoja@stonetrend.ca';

module.exports = async (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Access-Control-Allow-Origin', '*');

  if (req.method !== 'GET') {
    res.setHeader('Allow', 'GET');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  return res.status(200).json({
    formEmail: (process.env.FORM_EMAIL || DEFAULT_FORM_EMAIL).trim(),
  });
};
