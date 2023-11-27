import { ResponseContext, RequestContext, HttpFile, HttpInfo } from '../http/http';
import { Configuration} from '../configuration'
import { Observable, of, from } from '../rxjsStub';
import {mergeMap, map} from  '../rxjsStub';
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

import { ChatApiRequestFactory, ChatApiResponseProcessor} from "../apis/ChatApi";
export class ObservableChatApi {
    private requestFactory: ChatApiRequestFactory;
    private responseProcessor: ChatApiResponseProcessor;
    private configuration: Configuration;

    public constructor(
        configuration: Configuration,
        requestFactory?: ChatApiRequestFactory,
        responseProcessor?: ChatApiResponseProcessor
    ) {
        this.configuration = configuration;
        this.requestFactory = requestFactory || new ChatApiRequestFactory(configuration);
        this.responseProcessor = responseProcessor || new ChatApiResponseProcessor();
    }

    /**
     * Stream the response from the ChartGPT API.
     * Ask Chartgpt Stream
     * @param request 
     */
    public askChartgptStreamV1AskChartgptStreamPostWithHttpInfo(request: Request, _options?: Configuration): Observable<HttpInfo<Response>> {
        const requestContextPromise = this.requestFactory.askChartgptStreamV1AskChartgptStreamPost(request, _options);

        // build promise chain
        let middlewarePreObservable = from<RequestContext>(requestContextPromise);
        for (let middleware of this.configuration.middleware) {
            middlewarePreObservable = middlewarePreObservable.pipe(mergeMap((ctx: RequestContext) => middleware.pre(ctx)));
        }

        return middlewarePreObservable.pipe(mergeMap((ctx: RequestContext) => this.configuration.httpApi.send(ctx))).
            pipe(mergeMap((response: ResponseContext) => {
                let middlewarePostObservable = of(response);
                for (let middleware of this.configuration.middleware) {
                    middlewarePostObservable = middlewarePostObservable.pipe(mergeMap((rsp: ResponseContext) => middleware.post(rsp)));
                }
                return middlewarePostObservable.pipe(map((rsp: ResponseContext) => this.responseProcessor.askChartgptStreamV1AskChartgptStreamPostWithHttpInfo(rsp)));
            }));
    }

    /**
     * Stream the response from the ChartGPT API.
     * Ask Chartgpt Stream
     * @param request 
     */
    public askChartgptStreamV1AskChartgptStreamPost(request: Request, _options?: Configuration): Observable<Response> {
        return this.askChartgptStreamV1AskChartgptStreamPostWithHttpInfo(request, _options).pipe(map((apiResponse: HttpInfo<Response>) => apiResponse.data));
    }

    /**
     * Answer a user query using the ChartGPT API.
     * Ask Chartgpt
     * @param request 
     * @param stream 
     */
    public askChartgptV1AskChartgptPostWithHttpInfo(request: Request, stream?: any, _options?: Configuration): Observable<HttpInfo<Response>> {
        const requestContextPromise = this.requestFactory.askChartgptV1AskChartgptPost(request, stream, _options);

        // build promise chain
        let middlewarePreObservable = from<RequestContext>(requestContextPromise);
        for (let middleware of this.configuration.middleware) {
            middlewarePreObservable = middlewarePreObservable.pipe(mergeMap((ctx: RequestContext) => middleware.pre(ctx)));
        }

        return middlewarePreObservable.pipe(mergeMap((ctx: RequestContext) => this.configuration.httpApi.send(ctx))).
            pipe(mergeMap((response: ResponseContext) => {
                let middlewarePostObservable = of(response);
                for (let middleware of this.configuration.middleware) {
                    middlewarePostObservable = middlewarePostObservable.pipe(mergeMap((rsp: ResponseContext) => middleware.post(rsp)));
                }
                return middlewarePostObservable.pipe(map((rsp: ResponseContext) => this.responseProcessor.askChartgptV1AskChartgptPostWithHttpInfo(rsp)));
            }));
    }

    /**
     * Answer a user query using the ChartGPT API.
     * Ask Chartgpt
     * @param request 
     * @param stream 
     */
    public askChartgptV1AskChartgptPost(request: Request, stream?: any, _options?: Configuration): Observable<Response> {
        return this.askChartgptV1AskChartgptPostWithHttpInfo(request, stream, _options).pipe(map((apiResponse: HttpInfo<Response>) => apiResponse.data));
    }

}

import { HealthApiRequestFactory, HealthApiResponseProcessor} from "../apis/HealthApi";
export class ObservableHealthApi {
    private requestFactory: HealthApiRequestFactory;
    private responseProcessor: HealthApiResponseProcessor;
    private configuration: Configuration;

    public constructor(
        configuration: Configuration,
        requestFactory?: HealthApiRequestFactory,
        responseProcessor?: HealthApiResponseProcessor
    ) {
        this.configuration = configuration;
        this.requestFactory = requestFactory || new HealthApiRequestFactory(configuration);
        this.responseProcessor = responseProcessor || new HealthApiResponseProcessor();
    }

    /**
     * Ping the API to check if it is running.
     * Ping
     */
    public pingHealthGetWithHttpInfo(_options?: Configuration): Observable<HttpInfo<any>> {
        const requestContextPromise = this.requestFactory.pingHealthGet(_options);

        // build promise chain
        let middlewarePreObservable = from<RequestContext>(requestContextPromise);
        for (let middleware of this.configuration.middleware) {
            middlewarePreObservable = middlewarePreObservable.pipe(mergeMap((ctx: RequestContext) => middleware.pre(ctx)));
        }

        return middlewarePreObservable.pipe(mergeMap((ctx: RequestContext) => this.configuration.httpApi.send(ctx))).
            pipe(mergeMap((response: ResponseContext) => {
                let middlewarePostObservable = of(response);
                for (let middleware of this.configuration.middleware) {
                    middlewarePostObservable = middlewarePostObservable.pipe(mergeMap((rsp: ResponseContext) => middleware.post(rsp)));
                }
                return middlewarePostObservable.pipe(map((rsp: ResponseContext) => this.responseProcessor.pingHealthGetWithHttpInfo(rsp)));
            }));
    }

    /**
     * Ping the API to check if it is running.
     * Ping
     */
    public pingHealthGet(_options?: Configuration): Observable<any> {
        return this.pingHealthGetWithHttpInfo(_options).pipe(map((apiResponse: HttpInfo<any>) => apiResponse.data));
    }

}
