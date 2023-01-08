// v1: 28.12.2022 - 06.01.2023

import { createReadStream, readdirSync } from 'fs';
import { createInterface } from "readline";
import { getRootDir } from "./utils/misc.js";
import getBook from './getBook.js'



async function main() {

    const root = getRootDir();

    if (!readdirSync(root).includes('books.txt')) {
        console.log('File books.txt missing. Exiting...');
        return;
    }

    const rl = createInterface({
        input: createReadStream(root + '/books.txt')
    });

    let resourceKey = '';
    let first = true;

    for await (const line of rl) {

        if (first && line) {
            resourceKey = line;
            first = false;
        }
        
        if (!line.startsWith('https')) continue;

        await getBook(line, resourceKey);
    }
}

main();
