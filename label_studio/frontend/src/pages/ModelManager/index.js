import React, { useEffect, useState } from 'react';
import { ModelList } from "./ModelPage/ModelList";
import { Button } from '../../components';

export const ModelManagerPage = {
  title: t("Models Management"),
  path: "/model-configer",
  exact: true,
  layout: null,
  component: ModelList,
  pages: {},
  context:({ openModal, showButton }) => {
    if (!showButton) return null;
    return <Button onClick={openModal} look="primary" size="compact">{t("Import Model")}</Button>;
  },
};
