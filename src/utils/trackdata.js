import { parse } from 'node-html-parser';
import { getHTTPBody } from './url.js';



function removeForbiddenChars(str) {
    const forbidden = ['/', '\\', '<', '>', ':', '"', '|', '?', '*'];
    for (const c of forbidden) str = str.replaceAll(c, '');
    if (str.endsWith('.')) str = str.slice(0, str.length - 1);
    return str;
}

/**
 * Parses an audio book page and retrieves metadata of each track 
 * and then constructs track data objects and returns them in an array. 
 * @param {String} pageURL URL of the audiobook page.
 * @returns Promise resolving to array of track data objects.
 */
async function getTrackDataArray(pageURL) {

    const root = parse(await getHTTPBody(pageURL));
    
    const chapters = root.querySelectorAll('.chapter__default[data-pos]');
    const startTimes = chapters.map(c => c.getAttribute('data-pos'));

    const cb = (prev, curr) => `${prev}${prev ? ', ' : ''}${curr.innerText.trim()}`;
    const authors = root.querySelectorAll('span[itemprop="author"]').reduce(cb, '');
    const performers = root.querySelectorAll('a[rel="performer"]>span').reduce(cb, '');

    let album = root.querySelector('h1.caption__article-main').innerText.trim();
    album = removeForbiddenChars(album);

    let series = null;
    let trackIndex = null;

    if (chapters.length === 1) {
        let temp = root.querySelector('a.link__series>span');
        let parts = temp ? temp.innerText.split('(') : null;
        series = parts ? parts.shift().trim() : null;
        trackIndex = parts && parts.length ? parts.pop().replace(')', '') : 1;
    }

    let i = 0, j = 1;

    return chapters.map(c => {

        let title = c.querySelector('.chapter__default--title').innerText.trim();
        title = removeForbiddenChars(title);

        const start = startTimes[i];
        const end = j != startTimes.length ? startTimes[j] : null;

        i++; j++;

        return { title, start, end, album, authors, performers, series, trackIndex };
    });
}

export { getTrackDataArray };
