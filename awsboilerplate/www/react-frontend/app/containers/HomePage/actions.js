/*
 * Home Actions
 *
 * Actions change things in your application
 * Since this boilerplate uses a uni-directional data flow, specifically redux,
 * we have these actions which are the only way your application interacts with
 * your application state. This guarantees that your state is up to date and nobody
 * messes it up weirdly somewhere.
 *
 * To add a new Action:
 * 1) Import your constant
 * 2) Add a function like this:
 *    export function yourAction(var) {
 *        return { type: YOUR_ACTION_CONSTANT, var: var }
 *    }
 */

import {
  SUBMIT_BACKGROUND_JOB,
  BACKGROUND_JOB_ACCEPTED,
  BACKGROUND_JOB_LAUNCH_FAIL,
  BACKGROUND_JOB_STATUS_POLL, BACKGROUND_JOB_RESULT
} from './constants';

/**
 * Changes the input field of the form
 *
 * @param  {string} username The new text of the input field
 *
 * @return {object} An action object with a type of CHANGE_USERNAME
 */
export function submitBackgroundJob(number) {
  return {
    type: SUBMIT_BACKGROUND_JOB,
    number,
  };
}

export function backgroundJobAccepted(id, href, number) {
  return {
    type: BACKGROUND_JOB_ACCEPTED,
    id: id,
    href: href,
    number: number
  };
}

export function backgroundJobRejected(status) {
  return {
    type: BACKGROUND_JOB_LAUNCH_FAIL,
  };
}


export function pollCompletedJobs(status) {
  return {
    type: BACKGROUND_JOB_STATUS_POLL
  };
}

export function backgroundJobStatusResult(jobs_result) {
  return {
    type: BACKGROUND_JOB_RESULT,
    jobs_result: jobs_result
  };
}


