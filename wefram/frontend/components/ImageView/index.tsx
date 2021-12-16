import React from 'react'
import {
  Backdrop,
  Box, Button, IconButton, Image, MaterialIcon,
  Modal
} from 'system/components'
import {gettext} from 'system/l10n'
import {dialog} from 'system/dialog'
import {storage} from 'system/storage'


export type ImageViewProps = {
  src: string
  open: boolean
  onClose?: () => void
}


export const ImageView = (props: ImageViewProps) => (
  <Modal
    open={props.open}
    onClose={props.onClose}
  >
    <Backdrop
      open={props.open}
      style={{
        zIndex: 10000
      }}
    >
      <Box
        position={'absolute'}
        left={0}
        top={0}
        right={0}
        bottom={0}
        display={'flex'}
        justifyContent={'center'}
        alignItems={'center'}
        padding={'8px'}
      >
        <IconButton
          onClick={props.onClose}
          size={'small'}
          style={{
            color: '#ddd',
            position: 'absolute',
            right: '1vw',
            top: '1vw',
            zIndex: 2
          }}
        >
          <MaterialIcon icon={'close'} />
        </IconButton>
        <Image
          src={props.src}
          style={{
            backgroundColor: 'transparent',
            padding: undefined,
            paddingTop: undefined,
            position: 'absolute'
          }}
          imageStyle={{
            top: undefined,
            left: undefined,
            width: undefined,
            height: undefined,
            position: 'relative',
            overflow: 'hidden',
            maxWidth: 'calc(100vw - 16px)',
            maxHeight: 'calc(100vh - 16px)',
            borderRadius: '4px'
          }}
        />
      </Box>
    </Backdrop>
  </Modal>
)
