import { LaunchParams, retrieveLaunchParams } from "@telegram-apps/sdk";

const getLaunchParams = (): LaunchParams => {
  return retrieveLaunchParams();
};

export default getLaunchParams;

