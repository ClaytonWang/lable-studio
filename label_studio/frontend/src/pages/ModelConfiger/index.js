import React, { useEffect, useState } from 'react';
import { ModelList } from "./ModelPage/ModelList";
import { Button } from '../../components';
import { useContextProps } from '../../providers/RoutesProvider';
import { ModelImport } from "./ModelPage/ModelImport";
import { ModelExport } from "./ModelPage/ModelExport";

export const ModelConfigerPage = () => {
  const setContextProps = useContextProps();
  const [modal, setModal] = useState(false);
  const openModal = setModal.bind(null, true);
  const closeModal = setModal.bind(null, false);

  useEffect(() => {
    setContextProps({ openModal });
  }, []);

  return (
    <>
      <ModelList />
      { modal && <ModelImport onClose={closeModal} /> }
    </>
  );
};

ModelConfigerPage.title= t("Models Management");
ModelConfigerPage.path="/model-configer";
ModelConfigerPage.exact = true;

ModelConfigerPage.context = ({ openModal }) => {
  return <Button onClick={openModal} look="primary" size="compact">{t("Import Model")}</Button>;
};
