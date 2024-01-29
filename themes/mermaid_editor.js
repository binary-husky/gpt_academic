import { deflate, inflate } from '/file=themes/pako.esm.mjs';
import { toUint8Array, fromUint8Array, toBase64, fromBase64 } from '/file=themes/base64.mjs';

const base64Serde = {
    serialize: (state) => {
        return toBase64(state, true);
    },
    deserialize: (state) => {
        return fromBase64(state);
    }
};

const pakoSerde = {
    serialize: (state) => {
        const data = new TextEncoder().encode(state);
        const compressed = deflate(data, { level: 9 });
        return fromUint8Array(compressed, true);
    },
    deserialize: (state) => {
        const data = toUint8Array(state);
        return inflate(data, { to: 'string' });
    }
};

const serdes = {
    base64: base64Serde,
    pako: pakoSerde
};

export const serializeState = (state, serde = 'pako') => {
    if (!(serde in serdes)) {
        throw new Error(`Unknown serde type: ${serde}`);
    }
    const json = JSON.stringify(state);
    const serialized = serdes[serde].serialize(json);
    return `${serde}:${serialized}`;
};

const deserializeState = (state) => {
    let type, serialized;
    if (state.includes(':')) {
        let tempType;
        [tempType, serialized] = state.split(':');
        if (tempType in serdes) {
            type = tempType;
        } else {
            throw new Error(`Unknown serde type: ${tempType}`);
        }
    } else {
        type = 'base64';
        serialized = state;
    }
    const json = serdes[type].deserialize(serialized);
    return JSON.parse(json);
};