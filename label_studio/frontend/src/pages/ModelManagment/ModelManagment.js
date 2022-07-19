import React, { useEffect, useState } from 'react';
import { useParams as useRouterParams } from 'react-router';
import { Redirect } from 'react-router-dom';
import { Button } from '../../components';

export const ModelManagmentPage = () => {

};

export const ModelManagmentPage = {
  title: t("Models Management"),
  path: "/models",
  exact: true,
  layout: MenuLayout,
  component: PeoplePage,
  pages: {},
  context:({ openModal, showButton }) => {
    if (!showButton) return null;
    return <Button onClick={openModal} look="primary" size="compact">{t("Import Model")}</Button>;
  },
};
