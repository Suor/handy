// Microframework for reviving objects serialized by handy
JSON.revive = function (text) {
    return JSON.parse(text, JSON.reviver);
};

JSON.reviver = function reviver(key, value) {
    if (value && typeof value === 'object' && value._type) {
        return JSON.reviver[value._type](value);
    }
    return value;
};

JSON.reviver.date = function (value) {
    return new Date(value.ms);
};
