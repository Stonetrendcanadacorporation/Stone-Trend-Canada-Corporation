/**
 * Vercel serverless: create a Stripe PaymentIntent for checkout.
 * Set STRIPE_SECRET_KEY in Vercel environment variables.
 * POST body: { amount: number } (amount in cents)
 * Returns: { clientSecret: string }
 *
 * Enables: Visa, Mastercard, Amex, Discover, Apple Pay, Google Pay, PayPal
 * (Enable these in your Stripe Dashboard: Settings > Payment methods)
 */
const Stripe = require('stripe');

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const secretKey = process.env.STRIPE_SECRET_KEY;
  if (!secretKey) {
    return res.status(500).json({ error: 'Stripe not configured. Set STRIPE_SECRET_KEY in Vercel.' });
  }

  let amount;
  try {
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body || {};
    amount = Number(body.amount);
  } catch {
    return res.status(400).json({ error: 'Invalid JSON body' });
  }

  if (!Number.isInteger(amount) || amount < 50) {
    return res.status(400).json({ error: 'Amount must be at least 50 cents' });
  }

  const stripe = new Stripe(secretKey);

  try {
    const paymentIntent = await stripe.paymentIntents.create({
      amount: Math.round(amount),
      currency: 'cad',
      automatic_payment_methods: {
        enabled: true,
      },
    });
    return res.status(200).json({ clientSecret: paymentIntent.client_secret });
  } catch (err) {
    console.error('Stripe PaymentIntent error:', err.message);
    return res.status(500).json({ error: err.message || 'Failed to create payment intent' });
  }
};
