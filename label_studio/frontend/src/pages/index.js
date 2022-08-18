import { ProjectsPage } from './Projects/Projects';
import { ProjectCollection } from './ProjectCollection';
import { OrganizationPage } from './Organization';
import { ModelManagerPage } from './ModelManager';

const noOrg = APP_SETTINGS.user.noauth_page.some((v) => {
  return v.name === "organization";
});

const noModel = APP_SETTINGS.user.noauth_page.some((v) => {
  return v.name === "model";
});

const Pages = [
  ProjectsPage,
  ProjectCollection,
];

if (!noOrg) {
  Pages.push(OrganizationPage);
}

if (!noModel) {
  Pages.push(ModelManagerPage);
}

export { Pages };
