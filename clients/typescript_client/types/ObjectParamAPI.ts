import { ResponseContext, RequestContext, HttpFile, HttpInfo } from '../http/http';
import { Configuration} from '../configuration'

import { Attempt } from '../models/Attempt';
import { HTTPValidationError } from '../models/HTTPValidationError';
import { LocationInner } from '../models/LocationInner';
import { Message } from '../models/Message';
import { ModelError } from '../models/ModelError';
import { Output } from '../models/Output';
import { OutputType } from '../models/OutputType';
import { Request } from '../models/Request';
import { Response } from '../models/Response';
import { ResponseUsage } from '../models/ResponseUsage';
import { Role } from '../models/Role';
import { Status } from '../models/Status';
import { ValidationError } from '../models/ValidationError';

import { ObservableChatApi } from "./ObservableAPI";
import { ChatApiRequestFactory, ChatApiResponseProcessor} from "../apis/ChatApi";

export interface ChatApiAskChartgptStreamV1AskChartgptStreamPostRequest {
    /**
     * 
     * @type Request
     * @memberof ChatApiaskChartgptStreamV1AskChartgptStreamPost
     */
    request: Request
}

export interface ChatApiAskChartgptV1AskChartgptPostRequest {
    /**
     * 
     * @type Request
     * @memberof ChatApiaskChartgptV1AskChartgptPost
     */
    request: Request
    /**
     * 
     * @type any
     * @memberof ChatApiaskChartgptV1AskChartgptPost
     */
    stream?: any
}

export class ObjectChatApi {
    private api: ObservableChatApi

    public constructor(configuration: Configuration, requestFactory?: ChatApiRequestFactory, responseProcessor?: ChatApiResponseProcessor) {
        this.api = new ObservableChatApi(configuration, requestFactory, responseProcessor);
    }

    /**
     * Stream the response from the ChartGPT API.
     * Ask Chartgpt Stream
     * @param param the request object
     */
    public askChartgptStreamV1AskChartgptStreamPostWithHttpInfo(param: ChatApiAskChartgptStreamV1AskChartgptStreamPostRequest, options?: Configuration): Promise<HttpInfo<Response>> {
        return this.api.askChartgptStreamV1AskChartgptStreamPostWithHttpInfo(param.request,  options).toPromise();
    }

    /**
     * Stream the response from the ChartGPT API.
     * Ask Chartgpt Stream
     * @param param the request object
     */
    public askChartgptStreamV1AskChartgptStreamPost(param: ChatApiAskChartgptStreamV1AskChartgptStreamPostRequest, options?: Configuration): Promise<Response> {
        return this.api.askChartgptStreamV1AskChartgptStreamPost(param.request,  options).toPromise();
    }

    /**
     * Answer a user query using the ChartGPT API.
     * Ask Chartgpt
     * @param param the request object
     */
    public askChartgptV1AskChartgptPostWithHttpInfo(param: ChatApiAskChartgptV1AskChartgptPostRequest, options?: Configuration): Promise<HttpInfo<Response>> {
        return this.api.askChartgptV1AskChartgptPostWithHttpInfo(param.request, param.stream,  options).toPromise();
    }

    /**
     * Answer a user query using the ChartGPT API.
     * Ask Chartgpt
     * @param param the request object
     */
    public askChartgptV1AskChartgptPost(param: ChatApiAskChartgptV1AskChartgptPostRequest, options?: Configuration): Promise<Response> {
        return this.api.askChartgptV1AskChartgptPost(param.request, param.stream,  options).toPromise();
    }

}

import { ObservableHealthApi } from "./ObservableAPI";
import { HealthApiRequestFactory, HealthApiResponseProcessor} from "../apis/HealthApi";

export interface HealthApiPingHealthGetRequest {
}

export class ObjectHealthApi {
    private api: ObservableHealthApi

    public constructor(configuration: Configuration, requestFactory?: HealthApiRequestFactory, responseProcessor?: HealthApiResponseProcessor) {
        this.api = new ObservableHealthApi(configuration, requestFactory, responseProcessor);
    }

    /**
     * Ping the API to check if it is running.
     * Ping
     * @param param the request object
     */
    public pingHealthGetWithHttpInfo(param: HealthApiPingHealthGetRequest = {}, options?: Configuration): Promise<HttpInfo<any>> {
        return this.api.pingHealthGetWithHttpInfo( options).toPromise();
    }

    /**
     * Ping the API to check if it is running.
     * Ping
     * @param param the request object
     */
    public pingHealthGet(param: HealthApiPingHealthGetRequest = {}, options?: Configuration): Promise<any> {
        return this.api.pingHealthGet( options).toPromise();
    }

}
