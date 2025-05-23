

const axios = require('axios');
const cheerio = require('cheerio');

// Pinata configuration
const PINATA_API_KEY = '738b3cff0f55609173a9';
const PINATA_SECRET_API_KEY = '6008a9d5bd8120e13f42cad76b0cefdd24da2f07e00f9b5d74dd4de75f19ff0a';

// Ethics check
function isEthicalContent(content) {
  const bannedWords = ['malware', 'phishing', 'hate'];
  return !bannedWords.some(word => content.toLowerCase().includes(word));
}

// Fetch meta tags
async function getMetaInstructions() {
  try {
    const response = await axios.get('https://asinoro.github.io/SparkEthos/');
    const $ = cheerio.load(response.data);
    return $('meta[name="tn-instructions"]').attr('content') || 'No instructions';
  } catch (error) {
    console.error('Meta fetch error:', error);
    return 'Error fetching meta';
  }
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).send('Method not allowed');
  }

  const { content, from } = req.body;

  if (!content || !from) {
    return res.status(400).send('Missing content or sender');
  }

  if (!isEthicalContent(content)) {
    return res.status(403).send('Content violates ethical guidelines');
  }

  const instructions = await getMetaInstructions();

  try {
    const response = await axios.post('https://api.pinata.cloud/pinning/pinJSONToIPFS', {
      pinataContent: { content, from, instructions },
      pinataMetadata: { name: 'SparkEthosUpdate' }
    }, {
      headers: {
        'pinata_api_key': PINATA_API_KEY,
        'pinata_secret_api_key': PINATA_SECRET_API_KEY
      }
    });
    res.status(200).json({ cid: response.data.IpfsHash, instructions });
  } catch (error) {
    console.error('Pinata error:', error);
    res.status(500).send('Failed to store content');
  }
};
