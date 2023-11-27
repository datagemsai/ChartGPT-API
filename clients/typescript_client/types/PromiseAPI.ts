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
import { ObservableChatApi } from './ObservableAPI';

import { ChatApiRequestFactory, ChatApiResponseProcessor} from "../apis/ChatApi";
export class PromiseChatApi {
    private api: ObservableChatApi

    public constructor(
        configuration: Configuration,
        requestFactory?: ChatApiRequestFactory,
        responseProcessor?: ChatApiResponseProcessor
    ) {
        this.api = new ObservableChatApi(configuration, requestFactory, responseProcessor);
    }

    /**
     * Stream the response from the ChartGPT API.
     * Ask Chartgpt Stream
     * @param request 
     */
    public askChartgptStreamV1AskChartgptStreamPostWithHttpInfo(request: Request, _options?: Configuration): Promise<HttpInfo<Response>> {
        const result = this.api.askChartgptStreamV1AskChartgptStreamPostWithHttpInfo(request, _options);
        return result.toPromise();
    }

    /**
     * Stream the response from the ChartGPT API.
     * Ask Chartgpt Stream
     * @param request 
     */
    public askChartgptStreamV1AskChartgptStreamPost(request: Request, _options?: Configuration): Promise<Response> {
        const result = this.api.askChartgptStreamV1AskChartgptStreamPost(request, _options);
        return result.toPromise();
    }

    /**
     * Answer a user query using the ChartGPT API.
     * Ask Chartgpt
     * @param request 
     * @param stream 
     */
    public askChartgptV1AskChartgptPostWithHttpInfo(request: Request, stream?: any, _options?: Configuration): Promise<HttpInfo<Response>> {
        const result = this.api.askChartgptV1AskChartgptPostWithHttpInfo(request, stream, _options);
        return result.toPromise();
    }

    /**
     * Answer a user query using the ChartGPT API.
     * Ask Chartgpt
     * @param request 
     * @param stream 
     */
    public askChartgptV1AskChartgptPost(request: Request, stream?: any, _options?: Configuration): Promise<Response> {
        const result = this.api.askChartgptV1AskChartgptPost(request, stream, _options);
        return result.toPromise();
    }


}



import { ObservableHealthApi } from './ObservableAPI';

import { HealthApiRequestFactory, HealthApiResponseProcessor} from "../apis/HealthApi";
export class PromiseHealthApi {
    private api: ObservableHealthApi

    public constructor(
        configuration: Configuration,
        requestFactory?: HealthApiRequestFactory,
        responseProcessor?: HealthApiResponseProcessor
    ) {
        this.api = new ObservableHealthApi(configuration, requestFactory, responseProcessor);
    }

    /**
     * Ping the API to check if it is running.
     * Ping
     */
    public pingHealthGetWithHttpInfo(_options?: Configuration): Promise<HttpInfo<any>> {
        const result = this.api.pingHealthGetWithHttpInfo(_options);
        return result.toPromise();
    }

    /**
     * Ping the API to check if it is running.
     * Ping
     */
    public pingHealthGet(_options?: Configuration): Promise<any> {
        const result = this.api.pingHealthGet(_options);
        return result.toPromise();
    }


}



