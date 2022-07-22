import React, { useContext, useEffect,useState } from 'react';
import { ModelList } from "./ModelPage/ModelList";
import { Button } from '../../components';
import { useContextProps } from '../../providers/RoutesProvider';
import { ModelImport } from "./ModelPage/ModelImport";
import { ModelExport } from "./ModelPage/ModelExport";
import { Block, Elem } from '../../utils/bem';
import { CloudUploadOutlined } from '@ant-design/icons';
import { Oneof } from '../../components/Oneof/Oneof';
import { Loading } from '../../components';

import "./index.styl";


export const ModelManagerPage = () => {

  const setContextProps = useContextProps();

  const [modal, setModal] = useState(false);
  const openModal = setModal.bind(null, true);
  const closeModal = setModal.bind(null, false);


  useEffect(() => {
    setContextProps({ openModal });
  }, []);

  return (
    <Block name="models-page">
      <Elem name="content" case="loaded">
        <ModelList />
        { modal && <ModelImport onClose={closeModal} /> }
      </Elem>
    </Block>
  );
};

ModelManagerPage.title= t("Models Management");
ModelManagerPage.path="/model-manager";
ModelManagerPage.exact = true;

ModelManagerPage.context = ({ openModal }) => {
  return <Button onClick={openModal} look="primary" size="compact" icon={<CloudUploadOutlined style={{ width:20,height:20,marginLeft:-10 }} />}>{t("Import Model")}</Button>;
};
