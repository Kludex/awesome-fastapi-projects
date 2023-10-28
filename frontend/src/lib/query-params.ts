import { AppRouterInstance } from "next/dist/shared/lib/app-router-context";

export interface QueryParamsManagerInterface {
  requestQueryUpdate: (key: string, value: string) => void;
  requestQueryDelete: (key: string) => void;
  requestQueryClear: () => void;
  commit: () => void;
}

export class QueryParamsManager implements QueryParamsManagerInterface {
  constructor(
    private readonly router: AppRouterInstance,
    private readonly pathname: string,
    private readonly initialParams: URLSearchParams,
    private readonly _queue: Array<
      [key: string, value: string | null] | ["clear"]
    > = [],
    private readonly _internalState: Map<string, string> = new Map(),
  ) {
    this.initialParams.forEach((value, key) => {
      this._internalState.set(key, value);
    });
  }

  requestQueryUpdate(key: string, value: string) {
    this._queue.push([key, value]);
  }

  requestQueryDelete(key: string) {
    this._queue.push([key, null]);
  }

  requestQueryClear() {
    this._queue.push(["clear"]);
  }

  private _processQueue() {
    for (const request of this._queue) {
      if (request.length === 1) {
        const [command] = request;
        if (command === "clear") {
          this._internalState.clear();
        }
      } else {
        if (request.length === 2) {
          const [key, value] = request;
          if (value === null) {
            this._internalState.delete(key);
          } else {
            this._internalState.set(key, value);
          }
        }
      }
    }
    this._queue.length = 0;
  }

  commit() {
    this._processQueue();
    const params = new URLSearchParams();
    this._internalState.forEach((value, key) => {
      params.set(key, value);
    });
    const newUrl = `${this.pathname}?${params.toString()}`;
    this.router.replace(newUrl);
  }
}
