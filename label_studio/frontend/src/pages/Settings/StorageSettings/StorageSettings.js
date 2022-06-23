import React from 'react';
import { Columns } from '../../../components/Columns/Columns';
import { Description } from '../../../components/Description/Description';
import { Block, cn } from '../../../utils/bem';
import { StorageSet } from './StorageSet';
import './StorageSettings.styl';

export const StorageSettings = () => {
  const rootClass = cn("storage-settings");

  return (
    <Block name="storage-settings">
      <Description style={{ marginTop: 0 }}>
        {
          t("storage_add_tip")
        }
      </Description>

      <Columns count={2} gap="40px" size="320px" className={rootClass}>
        <StorageSet
          title={t("Source Cloud Storage")}
          buttonLabel={t("Add Source Storage")}
          rootClass={rootClass}
        />

        <StorageSet
          title={t("Target Cloud Storage")}
          target="export"
          buttonLabel={t("Add Target Storage")}
          rootClass={rootClass}
        />
      </Columns>
    </Block>
  );
};

StorageSettings.title = t("Cloud Storage");
StorageSettings.path = "/storage";
