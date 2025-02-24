/**
 * ChartGPT API
 * The ChartGPT API is a REST API that generates insights from data based on natural language questions.
 *
 * OpenAPI spec version: 0.1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import { LocationInner } from '../models/LocationInner';
import { HttpFile } from '../http/http';

export class ValidationError {
    'loc': Array<LocationInner>;
    'msg': string;
    'type': string;

    static readonly discriminator: string | undefined = undefined;

    static readonly attributeTypeMap: Array<{name: string, baseName: string, type: string, format: string}> = [
        {
            "name": "loc",
            "baseName": "loc",
            "type": "Array<LocationInner>",
            "format": ""
        },
        {
            "name": "msg",
            "baseName": "msg",
            "type": "string",
            "format": ""
        },
        {
            "name": "type",
            "baseName": "type",
            "type": "string",
            "format": ""
        }    ];

    static getAttributeTypeMap() {
        return ValidationError.attributeTypeMap;
    }

    public constructor() {
    }
}

