import { parse } from 'node-html-parser';
import https from 'https';



/**
 * Simple URL check.
 * @param {String} url 
 * @returns Promise which resolves to boolean.
 */
function isOK(url) {
    const i = url.indexOf('/', 8);
    const options = {
        host: url.substring(8, i),
        path: encodeURI(url.substring(i)),
        port: 443,
        method: 'HEAD'
    };

    return new Promise(resolve => {
        const req = https.request(options, res => {
            res.statusCode == 200 ? resolve(true) : resolve(false);
        });

        req.on('error', err => console.error(err));

        req.end();
    });
}

/**
 * Does it says what.
 * @param {String} url 
 * @returns String
 */
function getHTTPBody(url) {
    return new Promise(resolve => {
        https.get(url, res => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => resolve(body));
        });
    });
}

/**
 * Returns a valid resource URL or an empty string if no valid URL was found.
 * @param {String} pageURL URL of the audiobook page.
 * @param {String} resourceKey The secret part of a resource URL.
 * @returns Resource URL as string or empty string.
 */
async function getResourceURL(pageURL, resourceKey) {
    
    const body = await getHTTPBody(pageURL);

    const bookID = parse(body).querySelector('*[data-bid]').getAttribute('data-bid');
    const name = pageURL.split('/').pop();
    
    const subdomains = ['s0', 's1', 's2', 't0', 't1', 't2', 'm0', 'm1', 'm2'];

    for (const subdom of subdomains) {
        const url = `https://${subdom}.akniga.club/b/${bookID}/${resourceKey}/${name}.mp3`;
        if (await isOK(url)) return url
    }

    return '';
}

/**
 * Returns all audiobook page URLs of a series based on a series URL.
 * @param {String} seriesURL Of form https://akniga.org/series/(series_name)
 * @returns Array of all page URLs of a series.
 */
async function getPageURLs(seriesURL) {

    if (seriesURL.includes('/page')) {
        const parts = seriesURL.split('/');
        parts.pop();
        seriesURL = parts.join('/');
    }

    const seriesURLs = await getSeriesURLs(seriesURL);
    const pageURLs = [];

    for (const url of seriesURLs) {
        const root = parse(await getHTTPBody(url));
        const links = root.querySelectorAll('a.content__article-main-link').map(a => a.getAttribute('href'));
        pageURLs.push(links);
    }

    return pageURLs.flat();
}

async function getSeriesURLs(seriesURL) {
    const seriesURLs = [seriesURL];
    for (let i = 2; ;i++) {
        const next = seriesURL + '/page' + i;
        const root = parse(await getHTTPBody(next));
        const links = root.querySelectorAll('a.content__article-main-link');
        if (!links.length) break;
        seriesURLs.push(next);
    }
    return seriesURLs;
}

export { 
    isOK, 
    getHTTPBody, 
    getResourceURL, 
    getPageURLs 
};
